from .session import ServerProtocolSession


class ProtocolSessionRegistry:
    def __init__(self):
        self._sessions = []

    def add(self, session: ServerProtocolSession):
        self._sessions.append(session)

    def remove(self, session: ServerProtocolSession):
        self._sessions.remove(session)

    def get_session(self) -> ServerProtocolSession | None:
        return self._sessions[-1] if self._sessions else None
