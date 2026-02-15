from .session import ServerProtocolSession


class ProtocolSessionRegistry:
    def __init__(self):
        self._sessions: list[ServerProtocolSession] = []

    def add(self, session: ServerProtocolSession):
        self._sessions.append(session)

    def remove(self, session: ServerProtocolSession):
        self._sessions.remove(session)

    def get_newest_session(self) -> ServerProtocolSession | None:
        return self._sessions[-1] if self._sessions else None

    def get_session(self, datalogger_serial: str) -> ServerProtocolSession | None:
        for session in self._sessions:
            if session.state.datalogger_serial == datalogger_serial:
                return session
        return None

    def get_all_sessions(self) -> list[ServerProtocolSession]:
        return self._sessions.copy()
