from loguru import logger

from shine2mqtt.growatt.protocol.config import ConfigRegistry
from shine2mqtt.growatt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.growatt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.growatt.protocol.messages.base import BaseMessage
from shine2mqtt.growatt.server.protocol.event import ProtocolEvent
from shine2mqtt.growatt.server.protocol.queues import OutgoingFrames, ProtocolEvents
from shine2mqtt.growatt.server.protocol.session.command.handler import CommandHandler
from shine2mqtt.growatt.server.protocol.session.message.handler import MessageHandler
from shine2mqtt.growatt.server.protocol.session.state import ServerProtocolSessionState


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

        command_handler = CommandHandler(session_state, self.config_registry)
        message_handler = MessageHandler(session_state)

        return ServerProtocolSession(
            decoder=self.decoder,
            encoder=self.encoder,
            outgoing_frames=outgoing_frames,
            protocol_events=self.protocol_events,
            message_handler=message_handler,
            command_handler=command_handler,
        )


class ServerProtocolSession:
    def __init__(
        self,
        decoder: FrameDecoder,
        encoder: FrameEncoder,
        outgoing_frames: OutgoingFrames,
        protocol_events: ProtocolEvents,
        message_handler: MessageHandler,
        command_handler: CommandHandler,
    ):
        self.decoder = decoder
        self.encoder = encoder

        self.protocol_events = protocol_events
        self.outgoing_frames = outgoing_frames

        self.command_handler = command_handler
        self.message_handler = message_handler

    def handle_incoming_frame(self, frame: bytes) -> None:
        message: BaseMessage = self.decoder.decode(frame)

        self.command_handler.resolve_response(message)
        self._publish_protocol_event(message)

        response_messages = self.message_handler.handle_message(message)

        for response_message in response_messages:
            logger.info(
                f"Enqueue response {response_message.header.function_code.name} ({response_message.header.function_code.value:#02x})"
            )
            logger.debug(f"Response message content: {response_message}")

            outgoing_frame: bytes = self.encoder.encode(response_message)
            self.outgoing_frames.put_nowait(outgoing_frame)

    def _publish_protocol_event(self, message: BaseMessage):
        from shine2mqtt.growatt.protocol.messages.base import DataloggerMessage

        if isinstance(message, DataloggerMessage):
            event = ProtocolEvent(
                datalogger_serial=message.datalogger_serial,
                message=message,
            )
            self.protocol_events.put_nowait(event)

    def handle_command(self, command):
        if message := self.command_handler.handle_command(command):
            frame = self.encoder.encode(message)
            self.outgoing_frames.put_nowait(frame)
