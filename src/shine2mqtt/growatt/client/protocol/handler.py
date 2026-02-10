from collections.abc import Callable

from loguru import logger

from shine2mqtt.growatt.client.protocol.generator import FrameGenerator
from shine2mqtt.growatt.protocol.ack.ack import GrowattAckMessage
from shine2mqtt.growatt.protocol.base.message import BaseMessage
from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.get_config.get_config import (
    GrowattGetConfigRequestMessage,
)
from shine2mqtt.growatt.protocol.ping.message import GrowattPingMessage
from shine2mqtt.growatt.protocol.set_config.set_config import (
    GrowattSetConfigRequestMessage,
)


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

        match message:
            case GrowattAckMessage() if function_code == FunctionCode.ANNOUNCE:
                logger.info(
                    f"✓ Received ACK for ANNOUNCE ({hex_value}) response, datalogger is now ANNOUNCED!"
                )
                self._announce_callback(message) if self._announce_callback else None
            case GrowattAckMessage() if function_code == FunctionCode.DATA:
                logger.info(f"✓ Received ACK for DATA ({hex_value}) response")
            case GrowattAckMessage() if function_code == FunctionCode.BUFFERED_DATA:
                logger.info(f"✓ Received ACK for BUFFERED_DATA ({hex_value}) response")
            case GrowattPingMessage():
                logger.info(f"✓ Received PING ({hex_value}) response")
            case GrowattGetConfigRequestMessage():
                logger.info(f"✓ Received GET_CONFIG request ({hex_value})")
                return self._build_get_config_response_frame(message)
            case GrowattSetConfigRequestMessage():
                logger.info(f"✓ Received SET_CONFIG request ({hex_value})")
                return self._build_ack_frame(message)
            case _:
                logger.warning(f"Unhandled message type: {type(message)}")

    def _build_get_config_response_frame(
        self, request_message: GrowattGetConfigRequestMessage
    ) -> bytes:
        return self.generator.generate_get_config_response_frame(
            transaction_id=request_message.header.transaction_id,
            register=request_message.register_start,
        )

    def _build_ack_frame(self, request_message: GrowattSetConfigRequestMessage) -> bytes:
        return self.generator.generate_ack_frame(
            header=request_message.header,
            ack=True,
        )
