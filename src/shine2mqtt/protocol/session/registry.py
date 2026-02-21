from shine2mqtt.domain.interfaces.registry import SessionRegistry
from shine2mqtt.domain.interfaces.session import Session
from shine2mqtt.protocol.session.session import ProtocolSession


class ProtocolSessionRegistry(SessionRegistry):
    def __init__(self):
        self._sessions: dict[str, ProtocolSession] = {}

    def get(self, datalogger_serial: str) -> Session | None:
        return self._sessions.get(datalogger_serial, None)

    def get_all(self) -> list[Session]:
        return list(self._sessions.values())

    def add(self, session: ProtocolSession) -> None:
        self._sessions[session.datalogger.serial] = session

    def remove(self, session: ProtocolSession) -> None:
        self._sessions.pop(session.datalogger.serial, None)
