from shine2mqtt.protocol.protocol.base.message import BaseMessage
from shine2mqtt.protocol.server.protocol.session.command.command import BaseCommand
from shine2mqtt.protocol.server.protocol.session.session import ServerProtocolSession


class SessionCommandExecutor:
    def __init__(self, session: ServerProtocolSession):
        self._session = session

    async def execute[TMessage: BaseMessage](self, command: BaseCommand[TMessage]) -> TMessage:
        """Execute a command and wait for its response."""
        self._session.send_command(command)
        return await command.wait_for_response()
