from collections.abc import Callable

from shine2mqtt.protocol.frame.header.header import FunctionCode
from shine2mqtt.protocol.messages.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.messages.get_config.get_config import (
    GrowattGetConfigRequestMessage,
)
from shine2mqtt.protocol.messages.message import BaseMessage
from shine2mqtt.protocol.messages.ping.message import GrowattPingMessage
from shine2mqtt.protocol.messages.set_config.set_config import (
    GrowattSetConfigRequestMessage,
)
from shine2mqtt.protocol.simulator.generator import FrameGenerator
from shine2mqtt.util.logger import logger


class ClientMessageHandler:
    def __init__(
        self,
        generator: FrameGenerator,
        announce_callback: Callable[[GrowattAckMessage], None] | None = None,
    ):
        self.generator = generator
        self._announce_callback = announce_callback

    def set_announce_callback(self, callback: Callable[[GrowattAckMessage], None]) -> None:
        self._announce_callback = callback

    def handle_message(self, message: BaseMessage) -> bytes | None:
        function_code = message.header.function_code
        hex_value = f"0x{function_code.value:02x}"
        transaction_id = message.header.transaction_id

        match message:
            case GrowattAckMessage() if function_code == FunctionCode.ANNOUNCE:
                logger.info(
                    f"✓ Received ACK for ANNOUNCE ({hex_value}) response, {transaction_id=}, datalogger is now ANNOUNCED!"
                )
                self._announce_callback(message) if self._announce_callback else None
            case GrowattAckMessage() if function_code == FunctionCode.DATA:
                logger.info(f"✓ Received ACK for DATA ({hex_value}) response, {transaction_id=}")
            case GrowattAckMessage() if function_code == FunctionCode.BUFFERED_DATA:
                logger.info(
                    f"✓ Received ACK for BUFFERED_DATA ({hex_value}) response, {transaction_id=}"
                )
            case GrowattPingMessage():
                logger.info(f"✓ Received PING ({hex_value}) response, {transaction_id=}")
            case GrowattGetConfigRequestMessage():
                logger.info(f"✓ Received GET_CONFIG request ({hex_value}), {transaction_id=}")
                return self._build_get_config_response_frame(message)
            case GrowattSetConfigRequestMessage():
                logger.info(f"✓ Received SET_CONFIG request ({hex_value}), {transaction_id=}")
                return self._build_ack_frame(message)
            case _:
                logger.warning(f"Unhandled message type: {type(message)}")

    def _build_get_config_response_frame(
        self, request_message: GrowattGetConfigRequestMessage
    ) -> bytes:
        return self.generator.generate_get_config_response_frame(
            transaction_id=request_message.header.transaction_id,
            register=request_message.register_start,
            datalogger_serial=request_message.datalogger_serial,
        )

    def _build_ack_frame(self, request_message: GrowattSetConfigRequestMessage) -> bytes:
        return self.generator.generate_ack_frame(
            header=request_message.header,
            ack=True,
        )
