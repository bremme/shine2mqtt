from shine2mqtt.domain.interfaces.registry import SessionRegistry
from shine2mqtt.domain.interfaces.session import Session
from shine2mqtt.protocol.session.session import ProtocolSession


class ProtocolSessionRegistry(SessionRegistry):
    def __init__(self):
        self._sessions: list[ProtocolSession] = []

    def get(self, datalogger_serial: str) -> Session | None:
        for session in self._sessions:
            if session.datalogger_serial == datalogger_serial:
                return session
        return None

    def add(self, session: ProtocolSession) -> None:
        self._sessions.append(session)

    def remove(self, session: ProtocolSession) -> None:
        self._sessions.remove(session)
