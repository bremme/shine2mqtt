import asyncio
from asyncio import Future

from loguru import logger

from shine2mqtt.growatt.protocol.base.message import BaseMessage
from shine2mqtt.growatt.server.protocol.session.command.command import BaseCommand
from shine2mqtt.growatt.server.protocol.session.session import ServerProtocolSession, TransactionKey


class SessionCommandExecutor:
    def __init__(self, session: ServerProtocolSession):
        self._session = session
        self._pending_futures: dict[TransactionKey, Future[BaseMessage]] = {}

    async def execute(self, command: BaseCommand, timeout: float = 10.0) -> BaseMessage | None:  # noqa: S7483
        future: Future[BaseMessage] = Future()

        key = self._session.send_command(command, self._handle_response)

        self._pending_futures[key] = future

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except TimeoutError:
            self._pending_futures.pop(key, None)
            raise

    def _handle_response(self, key: TransactionKey, message: BaseMessage) -> None:
        if future := self._pending_futures.pop(key, None):
            if future.done():
                logger.warning(
                    f"Command future already done (likely cancelled/timeout) for transaction key {key}"
                )
                return
            future.set_result(message)


# class SessionCommandExecutor:
#     def __init__(
#         self, protocol_commands: ProtocolCommands, session_registry: ProtocolSessionRegistry
#     ):
#         self.protocol_commands = protocol_commands
#         self.session_registry = session_registry

#     async def run(self):
#         await asyncio.gather(self._command_listener_loop())

#     async def _command_listener_loop(self):
#         while True:
#             command = await self.protocol_commands.get()
#             logger.info(f"Received protocol command {command}, routing to session handler")
#             session = self.session_registry.get_session(command.datalogger_serial)

#             if session is None:
#                 logger.warning(
#                     f"No active protocol session found for command {command}, discarding command"
#                 )
#                 continue
#             session.handle_command(command)
