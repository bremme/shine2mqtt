import asyncio

from loguru import logger

from shine2mqtt.app.queues import (
    IncomingFrames,
    OutgoingFrames,
    ProtocolCommands,
    ProtocolEvents,
)
from shine2mqtt.growatt.protocol.config import ConfigRegistry
from shine2mqtt.growatt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.growatt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.growatt.protocol.processor.command.command import (
    BaseCommand,
)
from shine2mqtt.growatt.protocol.processor.command.handler import CommandHandler
from shine2mqtt.growatt.protocol.processor.message.handler import MessageHandler
from shine2mqtt.growatt.protocol.processor.state import SessionState


class ProtocolCoordinator:
    # _GET_CONFIG_REGISTER_START = 0
    # _GET_CONFIG_REGISTER_END = 61

    def __init__(
        self,
        decoder: FrameDecoder,
        encoder: FrameEncoder,
        incoming_frames: IncomingFrames,
        outgoing_frames: OutgoingFrames,
        protocol_commands: ProtocolCommands,
        protocol_events: ProtocolEvents,
    ):
        self.decoder = decoder
        self.encoder = encoder
        self.incoming_frames = incoming_frames
        self.outgoing_frames = outgoing_frames
        self.protocol_commands = protocol_commands
        self.protocol_events = protocol_events

        config_registry = ConfigRegistry()
        self.session_state = SessionState()

        self.command_handler = CommandHandler(self.session_state, config_registry)
        self.message_handler = MessageHandler(self.session_state)

    async def run(self):
        try:
            await asyncio.gather(self._frame_processor_loop(), self._command_processor_loop())
        finally:
            logger.info("Protocol coordinator fully closed")

    def reset(self):
        self.session_state.reset()
        self.message_handler.reset()
        self.command_handler.reset()

    async def _frame_processor_loop(self):
        while True:
            frame: bytes = await self.incoming_frames.get()

            message = self.decoder.decode(frame)

            self.command_handler.resolve_response(message)

            response_messages = self.message_handler.handle_message(message)

            for response_message in response_messages:
                logger.info(
                    f"Enqueue response {response_message.header.function_code.name} ({response_message.header.function_code.value:#02x})"
                )
                logger.debug(f"Response message content: {response_message}")

                outgoing_frame: bytes = self.encoder.encode(response_message)
                self.outgoing_frames.put_nowait(outgoing_frame)

            self.protocol_events.put_nowait(message)

    async def _command_processor_loop(self):
        while True:
            command: BaseCommand = await self.protocol_commands.get()
            logger.debug(f"Processing command: {command}")

            if message := self.command_handler.handle_command(command):
                frame = self.encoder.encode(message)
                self.outgoing_frames.put_nowait(frame)
