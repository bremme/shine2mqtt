from typing import Protocol

from shine2mqtt.domain.interfaces.session import Session


class SessionRegistry(Protocol):
    def get(self, datalogger_serial: str) -> Session | None: ...
    def get_all(self) -> list[Session]: ...
