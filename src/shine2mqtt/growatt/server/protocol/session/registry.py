from .session import ServerProtocolSession


class ProtocolSessionRegistry:
    def __init__(self):
        self._sessions = []

    def add(self, session: ServerProtocolSession):
        self._sessions.append(session)

    def get_session(self) -> ServerProtocolSession:
        return self._sessions[0]
