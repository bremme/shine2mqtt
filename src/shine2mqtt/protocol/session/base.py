from shine2mqtt.infrastructure.server.session import TCPSession
from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.messages.message import BaseMessage, DataloggerMessage
from shine2mqtt.util.logger import logger


class BaseProtocolSession:
    def __init__(self, transport: TCPSession, encoder: FrameEncoder, decoder: FrameDecoder):
        self.transport = transport
        self.encoder = encoder
        self.decoder = decoder

    async def _read_message(self) -> BaseMessage | None:
        frame = await self.transport.read_frame()
        try:
            message = self.decoder.decode(frame)
        except Exception as e:
            logger.error(f"Failed to decode incoming frame {frame}: {e}")
            return None

        if isinstance(message, DataloggerMessage):
            transaction_id = message.header.transaction_id
            datalogger_serial = message.datalogger_serial
            logger.info(
                f"✓ Receive {message.header.function_code.name} ({message.header.function_code.value:#02x}) message, {transaction_id=}, {datalogger_serial=}"
            )

        return message

    async def _write_message(self, response: BaseMessage) -> None:
        transaction_id = response.header.transaction_id
        logger.info(
            f"→ Send {response.header.function_code.name} ({response.header.function_code.value:#02x}) response, {transaction_id=}"
        )
        frame = self.encoder.encode(response)
        await self.transport.write_frame(frame)
