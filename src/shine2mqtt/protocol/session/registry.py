from typing import override

from shine2mqtt.domain.interfaces.registry import SessionRegistry
from shine2mqtt.domain.interfaces.session import Session


class ProtocolSessionRegistry(SessionRegistry):
    def __init__(self):
        self._sessions: dict[str, Session] = {}

    @override
    def get(self, datalogger_serial: str) -> Session | None:
        return self._sessions.get(datalogger_serial, None)

    @override
    def get_all(self) -> list[Session]:
        return list(self._sessions.values())

    @override
    def add(self, session: Session) -> None:
        self._sessions[session.datalogger.serial] = session

    @override
    def remove(self, session: Session) -> None:
        self._sessions.pop(session.datalogger.serial, None)
