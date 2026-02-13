import asyncio

from loguru import logger

from shine2mqtt.growatt.server.protocol.queues import ProtocolCommands
from shine2mqtt.growatt.server.protocol.session.registry import ProtocolSessionRegistry


class CommandRouter:
    def __init__(
        self, protocol_commands: ProtocolCommands, session_registry: ProtocolSessionRegistry
    ):
        self.protocol_commands = protocol_commands
        self.session_registry = session_registry

    async def run(self):
        await asyncio.gather(self._command_listener_loop())

    async def _command_listener_loop(self):
        while True:
            command = await self.protocol_commands.get()
            logger.info(f"Received protocol command {command}, routing to session handler")
            # TODO get session by datalogger serial
            session = self.session_registry.get_session()

            if session is None:
                logger.warning(
                    f"No active protocol session found for command {command}, discarding command"
                )
                continue
            session.handle_command(command)
