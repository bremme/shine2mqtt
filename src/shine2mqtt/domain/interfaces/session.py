from abc import abstractmethod
from typing import Protocol

from shine2mqtt.domain.models.datalogger import DataLogger


class Session(Protocol):
    @property
    @abstractmethod
    def data_logger(self) -> DataLogger:
        pass

    @abstractmethod
    async def read_register(self, address: int, timeout: float = 10.0) -> int:
        pass

    @abstractmethod
    async def write_register(self, address: int, value: int, timeout: float = 10.0) -> None:
        pass
