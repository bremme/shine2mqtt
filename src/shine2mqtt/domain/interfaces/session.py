from abc import ABC, abstractmethod

from shine2mqtt.domain.models.datalogger import DataLogger


class Session(ABC):
    @property
    @abstractmethod
    def datalogger(self) -> DataLogger | None:
        pass

    # @abstractmethod
    # async def read_register(self, address: int, timeout: float = 10.0) -> int:
    #     pass

    # @abstractmethod
    # async def write_register(self, address: int, value: int, timeout: float = 10.0) -> None:
    #     pass
