from asyncio import StreamReader, StreamWriter

from shine2mqtt.util.logger import logger


class TCPSession:
    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self._reader = reader
        self._writer = writer

    async def read(self, num_bytes: int) -> bytes:
        return await self._reader.readexactly(num_bytes)

    async def write(self, frame: bytes):
        self._writer.write(frame)
        await self._writer.drain()

    async def close(self):
        logger.info("Closing TCP session")
        self._writer.close()
        await self._writer.wait_closed()
