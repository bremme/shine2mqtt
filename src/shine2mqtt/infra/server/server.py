import asyncio
from asyncio import StreamReader, StreamWriter

from shine2mqtt.util.logger import logger


class TCPServer:
    def __init__(self):
        self.host = ""
        self.port = 0
        self.server = None

    async def start(self):
        logger.info("Creating TCP server")
        self.server = await asyncio.start_server(
            self._handle_client, host=self.host, port=self.port
        )

    async def serve(self):
        if self.server is None:
            raise RuntimeError("Server not started. Call start() first.")

        logger.info(f"Starting TCP server on {self.host}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    async def _handle_client(self, reader: StreamReader, writer: StreamWriter):
        addr = writer.get_extra_info("peername")

        logger.info(f"Accepted new TCP connection from {addr}")
