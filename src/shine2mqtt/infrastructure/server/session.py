from asyncio import StreamReader, StreamWriter

from shine2mqtt.protocol.frame.constants import HEADER_LENGTH
from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.util.logger import logger


class TCPSession:
    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.reader = reader
        self.writer = writer

    async def read_frame(self) -> bytes:
        raw_header = await self.reader.readexactly(HEADER_LENGTH)

        raw_payload_length = FrameDecoder.extract_payload_length(raw_header)

        raw_payload = await self.reader.readexactly(raw_payload_length)

        return raw_header + raw_payload

    async def write_frame(self, frame: bytes):
        self.writer.write(frame)
        await self.writer.drain()

    async def close(self):
        logger.info("Closing TCP session")
        self.writer.close()
        await self.writer.wait_closed()
