from loguru import logger

from shine2mqtt.protocol.protocol.announce.announce import GrowattAnnounceMessage
from shine2mqtt.protocol.protocol.base.message import BaseMessage, DataloggerMessage
from shine2mqtt.protocol.protocol.config import ConfigRegistry
from shine2mqtt.protocol.protocol.constants import FunctionCode
from shine2mqtt.protocol.protocol.data.data import GrowattBufferedDataMessage, GrowattDataMessage
from shine2mqtt.protocol.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.protocol.get_config.get_config import GrowattGetConfigResponseMessage
from shine2mqtt.protocol.protocol.ping.message import GrowattPingMessage
from shine2mqtt.protocol.protocol.read_register.read_register import (
    GrowattReadRegisterResponseMessage,
)
from shine2mqtt.protocol.protocol.set_config.set_config import GrowattSetConfigResponseMessage
from shine2mqtt.protocol.server.protocol.event import ProtocolEvent
from shine2mqtt.protocol.server.protocol.queues import OutgoingFrames, ProtocolEvents
from shine2mqtt.protocol.server.protocol.session.command.command import (
    BaseCommand,
    GetConfigByNameCommand,
    GetConfigByRegisterCommand,
    RawFrameCommand,
    ReadRegistersCommand,
    SetConfigByRegisterCommand,
)
from shine2mqtt.protocol.server.protocol.session.command.message_builder import (
    CommandMessageBuilder,
)
from shine2mqtt.protocol.server.protocol.session.message.handler import MessageHandler
from shine2mqtt.protocol.server.protocol.session.state import ServerProtocolSessionState


class ServerProtocolSessionFactory:
    def __init__(
        self,
        decoder: FrameDecoder,
        encoder: FrameEncoder,
        config_registry: ConfigRegistry,
        protocol_events: ProtocolEvents,
    ):
        self.decoder = decoder
        self.encoder = encoder
        self.config_registry = config_registry
        self.protocol_events = protocol_events

    def create(self) -> ServerProtocolSession:
        session_state = ServerProtocolSessionState()
        outgoing_frames = OutgoingFrames()

        command_handler = CommandMessageBuilder(session_state, self.config_registry)
        message_handler = MessageHandler(session_state)

        return ServerProtocolSession(
            decoder=self.decoder,
            encoder=self.encoder,
            outgoing_frames=outgoing_frames,
            protocol_events=self.protocol_events,
            message_handler=message_handler,
            command_handler=command_handler,
        )


type TransactionKey = tuple[FunctionCode, int]


class ServerProtocolSession:
    def __init__(
        self,
        decoder: FrameDecoder,
        encoder: FrameEncoder,
        outgoing_frames: OutgoingFrames,
        protocol_events: ProtocolEvents,
        message_handler: MessageHandler,
        command_handler: CommandMessageBuilder,
    ):
        self.decoder = decoder
        self.encoder = encoder

        self.protocol_events = protocol_events
        self.outgoing_frames = outgoing_frames

        self.command_message_builder = command_handler
        self.message_handler = message_handler

        self.pending_commands: dict[TransactionKey, BaseCommand] = {}

    @property
    def state(self) -> ServerProtocolSessionState:
        return self.message_handler.session_state

    def handle_incoming_frame(self, frame: bytes) -> None:
        try:
            message: BaseMessage = self.decoder.decode(frame)
        except Exception as e:
            logger.error(f"Failed to decode incoming frame {frame}: {e}")
            return

        transaction_id = message.header.transaction_id
        logger.info(
            f"✓ Receive {message.header.function_code.name} ({message.header.function_code.value:#02x}) message, {transaction_id=}"
        )

        self._publish_protocol_event(message)

        response_messages: list[BaseMessage] = []

        match message:
            # periodic datalogger messages
            case GrowattAnnounceMessage():
                response_messages = self.message_handler.build_announce_response(message)
            case GrowattDataMessage():
                response_messages = self.message_handler.build_data_response(message)
            case GrowattBufferedDataMessage():
                response_messages = self.message_handler.build_buffered_data_response(message)
            case GrowattPingMessage():
                response_messages = self.message_handler.build_ping_response(message)
            # datalogger response messages
            case GrowattGetConfigResponseMessage():
                self._complete_command(message)
            case GrowattSetConfigResponseMessage():
                self._complete_command(message)
            # inverter response messages
            case GrowattReadRegisterResponseMessage():
                self._complete_command(message)
            case _:
                logger.warning(
                    f"Received message with unhandled type {type(message)}, content: {message}"
                )

        for response_message in response_messages:
            transaction_id = response_message.header.transaction_id
            logger.info(
                f"→ Enqueue {response_message.header.function_code.name} ({response_message.header.function_code.value:#02x}) response, {transaction_id=}"
            )
            logger.debug(f"Response message content: {response_message}")

            outgoing_frame: bytes = self.encoder.encode(response_message)
            self.outgoing_frames.put_nowait(outgoing_frame)

    def send_command(self, command: BaseCommand):
        """Send a command and register it for response handling."""
        match command:
            case GetConfigByNameCommand():
                message = self.command_message_builder.build_get_config_message_by_name(
                    register_name=command.name,
                )
            case GetConfigByRegisterCommand():
                message = self.command_message_builder.build_get_config_message(
                    register_start=command.register,
                )
            case SetConfigByRegisterCommand():
                message = self.command_message_builder.build_set_config_message(
                    register=command.register, value=command.value
                )
            case RawFrameCommand():
                message = self.command_message_builder.build_raw_frame_message(command)

            case ReadRegistersCommand():
                message = self.command_message_builder.build_read_registers_message(command)
            case _:
                raise ValueError(f"Unknown command type: {type(command)}")

        transaction_id = message.header.transaction_id
        logger.info(
            f"→ Enqueue {message.header.function_code.name} ({message.header.function_code.value:#02x}) message for command {command.__class__.__name__}, {transaction_id=}"
        )

        self._add_pending_command(message, command)

        frame = self.encoder.encode(message)
        self.outgoing_frames.put_nowait(frame)

    def _publish_protocol_event(self, message: BaseMessage):
        if isinstance(message, DataloggerMessage):
            event = ProtocolEvent(
                datalogger_serial=message.datalogger_serial,
                message=message,
            )
            self.protocol_events.put_nowait(event)

    def _complete_command(self, message: BaseMessage) -> None:
        """Complete a pending command with the received response message."""
        if command := self._pop_pending_command(message):
            command.complete_with_response(message)
        else:
            logger.warning(
                f"Received response for unknown command with key {self._get_message_key(message)}"
            )

    def _add_pending_command(self, message: BaseMessage, command: BaseCommand) -> None:
        key = self._get_message_key(message)
        self.pending_commands[key] = command

    def _pop_pending_command(self, message: BaseMessage) -> BaseCommand | None:
        key = self._get_message_key(message)
        return self.pending_commands.pop(key, None)

    def _get_message_key(self, message: BaseMessage) -> TransactionKey:
        return (message.header.function_code, message.header.transaction_id)
