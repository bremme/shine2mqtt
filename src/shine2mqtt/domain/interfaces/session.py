from abc import ABC, abstractmethod

from shine2mqtt.domain.models.config import ConfigResult
from shine2mqtt.domain.models.datalogger import DataLogger


class Session(ABC):
    @property
    @abstractmethod
    def datalogger(self) -> DataLogger:
        pass

    @abstractmethod
    async def get_config(self, register: int) -> ConfigResult:
        pass

    @abstractmethod
    async def set_config(self, register: int, value: str) -> bool:
        pass

    @abstractmethod
    async def read_registers(self, register_start: int, register_end: int) -> dict[int, int]:
        pass

    @abstractmethod
    async def send_raw_frame(self, function_code: int, payload: bytes) -> bytes:
        pass
