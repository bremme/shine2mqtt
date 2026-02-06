import asyncio

from loguru import logger

from shine2mqtt.growatt.protocol.frame.decoder import HEADER_LENGTH, FrameDecoder


class TCPTransport:
    def __init__(self):
        self.reader = None
        self.writer = None

    async def connect(self, host: str, port: int):
        logger.info(f"Connecting to {host}:{port}")
        self.reader, self.writer = await asyncio.open_connection(host, port)
        logger.info("Connected to server")

    async def close(self):
        if self.writer:
            logger.info("Closing connection")
            self.writer.close()
            await self.writer.wait_closed()
            logger.info("Connection closed")

    async def write(self, frame: bytes) -> None:
        if not self.writer:
            raise RuntimeError("Not connected")

        self.writer.write(frame)
        await self.writer.drain()

    async def read(self) -> bytes:
        if not self.reader:
            raise RuntimeError("Not connected")

        raw_header = await self.reader.readexactly(HEADER_LENGTH)

        raw_payload_length = FrameDecoder.extract_payload_length(raw_header)

        raw_payload = await self.reader.readexactly(raw_payload_length)

        return raw_header + raw_payload
