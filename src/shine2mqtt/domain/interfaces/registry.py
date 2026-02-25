from abc import ABC, abstractmethod

from shine2mqtt.domain.interfaces.session import Session


class SessionRegistry(ABC):
    @abstractmethod
    def get(self, datalogger_serial: str) -> Session | None: ...

    @abstractmethod
    def get_all(self) -> list[Session]: ...

    @abstractmethod
    def add(self, session: Session) -> None: ...

    @abstractmethod
    def remove(self, session: Session) -> None: ...
