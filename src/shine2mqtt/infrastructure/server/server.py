import asyncio
from asyncio import StreamReader, StreamWriter
from typing import Any

from shine2mqtt.infrastructure.server.config import GrowattServerConfig
from shine2mqtt.infrastructure.server.session import TCPSession
from shine2mqtt.protocol.session.registry import ProtocolSessionRegistry
from shine2mqtt.protocol.session.session import ProtocolSessionFactory
from shine2mqtt.util.logger import logger


class TCPServer:
    def __init__(
        self,
        session_registry: ProtocolSessionRegistry,
        session_factory: ProtocolSessionFactory,
        config: GrowattServerConfig,
    ):
        self.session_registry = session_registry
        self.session_factory = session_factory
        self.host = config.host
        self.port = config.port
        self.server = None
        self.session_tasks: set[asyncio.Task[Any]] = set()
        self.stop_event = asyncio.Event()

    async def serve(self):
        await self._start_server()
        try:
            await self.stop_event.wait()
        finally:
            await self._close_sessions()
            await self._close_server()

    def stop(self):
        logger.info("Stopping TCP server using stop event")
        self.stop_event.set()

    async def _handle_client(self, reader: StreamReader, writer: StreamWriter):
        addr = writer.get_extra_info("peername")

        logger.info(f"Accepted new TCP connection from {addr}")

        transport = TCPSession(reader, writer)

        session = self.session_factory.create(transport=transport)

        self.session_registry.add(session)

        task = asyncio.current_task()
        assert task is not None
        self.session_tasks.add(task)

        try:
            logger.info(f"Starting TCP session for {addr}")
            await session.run()
        except Exception:
            logger.error(f"Error in TCP session from {addr}")
        finally:
            await session.close()
            logger.info(f"TCP session closed from {addr}")
            self.session_registry.remove(session)
            self.session_tasks.discard(task)

    async def _start_server(self):
        logger.info(f"Starting TCP server on {self.host}:{self.port}")
        self.server = await asyncio.start_server(self._handle_client, self.host, self.port)
        logger.info(
            f"TCP server is {'serving' if self.server.is_serving() else 'NOT serving'} on {self.host}:{self.port}"
        )

    async def _close_sessions(self):
        logger.info("Closing active TCP sessions")
        for i, task in enumerate(self.session_tasks):
            logger.info(f"Cancelling session {i} task '{task.get_name()}'")
            task.cancel()

        try:
            await asyncio.wait_for(asyncio.gather(*self.session_tasks), timeout=1.0)
        except TimeoutError:
            logger.warning("TCP session cancellation timed out")

        logger.info("All Active TCP sessions closed")

    async def _close_server(self):
        if not self.server:
            return
        logger.info("Closing TCP server")
        self.server.close()
        await self.server.wait_closed()
        logger.info("TCP server was closed")
