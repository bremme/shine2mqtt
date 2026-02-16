import asyncio
from asyncio import Future
from dataclasses import dataclass, field

from shine2mqtt.growatt.protocol.base.message import BaseMessage
from shine2mqtt.growatt.protocol.get_config.get_config import GrowattGetConfigResponseMessage
from shine2mqtt.growatt.protocol.raw.raw import GrowattRawMessage
from shine2mqtt.growatt.protocol.read_register.read_register import (
    GrowattReadRegisterResponseMessage,
)
from shine2mqtt.growatt.protocol.set_config.set_config import GrowattSetConfigResponseMessage


@dataclass
class BaseCommand[TMessage: BaseMessage]:
    datalogger_serial: str
    _future: Future[TMessage] = field(default_factory=Future, init=False, repr=False)

    async def wait_for_response(self, timeout: float) -> TMessage:  # noqa: S7483
        """Wait for the command response with timeout."""
        return await asyncio.wait_for(self._future, timeout)

    def complete_with_response(self, message: TMessage) -> None:
        """Complete the command with the received response message."""
        if not self._future.done():
            self._future.set_result(message)

    def complete_with_exception(self, exception: Exception) -> None:
        """Complete the command with an exception."""
        if not self._future.done():
            self._future.set_exception(exception)


@dataclass
class GetConfigByNameCommand(BaseCommand[GrowattGetConfigResponseMessage]):
    name: str


@dataclass
class SetConfigByNameCommand(BaseCommand[GrowattSetConfigResponseMessage]):
    name: str
    value: str


@dataclass
class GetConfigByRegistersCommand(BaseCommand[GrowattGetConfigResponseMessage]):
    register: int


@dataclass
class ReadRegistersCommand(BaseCommand[GrowattReadRegisterResponseMessage]):
    register_start: int
    register_end: int


@dataclass
class RawFrameCommand(BaseCommand[GrowattRawMessage]):
    function_code: int
    protocol_id: int
    payload: bytes
