import asyncio
from typing import Any

from shine2mqtt.domain.models.config import ConfigResult
from shine2mqtt.protocol.frame.header.header import FunctionCode
from shine2mqtt.protocol.messages.get_config.get_config import GrowattGetConfigResponseMessage
from shine2mqtt.protocol.messages.message import BaseMessage
from shine2mqtt.protocol.messages.raw.raw import GrowattRawRequestMessage
from shine2mqtt.protocol.messages.read_register.read_register import (
    GrowattReadMultipleRegisterResponseMessage,
)
from shine2mqtt.protocol.messages.set_config.set_config import GrowattSetConfigResponseMessage
from shine2mqtt.protocol.messages.write_register.write_register import (
    GrowattWriteMultipleRegistersResponseMessage,
    GrowattWriteSingleRegisterResponseMessage,
)
from shine2mqtt.util.logger import logger

type TransactionKey = tuple[FunctionCode, int]


class PendingResponseTracker:
    def __init__(self):
        self._pending_responses: dict[TransactionKey, asyncio.Future[Any]] = {}

    def track(self, request: BaseMessage) -> asyncio.Future[Any]:
        key = self._get_transaction_key(request)
        future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        self._pending_responses[key] = future
        return future

    def resolve(self, message: BaseMessage) -> None:
        key = self._get_transaction_key(message)
        response = self._pending_responses.pop(key, None)

        if response is None:
            logger.warning(f"Received unexpected response: {message}")
            return

        match message:
            case GrowattGetConfigResponseMessage():
                response.set_result(
                    ConfigResult(
                        register=message.register,
                        value=message.value,
                        raw_data=message.data,
                        name=message.name,
                    )
                )
            case GrowattSetConfigResponseMessage():
                response.set_result(message.ack)
            case GrowattReadMultipleRegisterResponseMessage():
                response.set_result(message.data_u16)
            case GrowattWriteSingleRegisterResponseMessage():
                response.set_result(message.ack)
            case GrowattWriteMultipleRegistersResponseMessage():
                response.set_result(message.ack)
            case GrowattRawRequestMessage():
                response.set_result(message.payload)
            case _:
                logger.warning(f"Received unhandled response message: {message}")

    def _get_transaction_key(self, message: BaseMessage) -> TransactionKey:
        return (message.header.function_code, message.header.transaction_id)
