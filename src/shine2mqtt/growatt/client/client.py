import asyncio
from asyncio import CancelledError, IncompleteReadError

from loguru import logger

from shine2mqtt.growatt.client.config import SimulatedClientConfig
from shine2mqtt.growatt.client.protocol.session import (
    ClientProtocolSession,
    ClientProtocolSessionFactory,
)
from shine2mqtt.growatt.client.transport import TCPTransport
from shine2mqtt.growatt.protocol.frame.factory import FrameFactory
from shine2mqtt.util.clock import MonotonicClockService


class SimulatedClient:
    """Simulated Growatt datalogger client that connects to a server, announces itself, and periodically sends data frames."""

    RETRY_DELAY = 2

    def __init__(self, config: SimulatedClientConfig):
        self.config = config
        self.client = TCPTransport()

        encoder = FrameFactory.encoder()
        decoder = FrameFactory.client_decoder()
        clock = MonotonicClockService()

        self.session_factory = ClientProtocolSessionFactory(
            encoder=encoder,
            decoder=decoder,
            config=config,
            clock=clock,
        )

    async def run(self):
        while True:
            try:
                await self.client.connect(self.config.server_host, self.config.server_port)

                logger.info("Starting protocol session")
                session = self.session_factory.create()

                await asyncio.gather(
                    self._receive_loop(session),
                    self._send_loop(session),
                )
            except (IncompleteReadError, ConnectionRefusedError) as e:
                logger.warning(f"Connection lost or failed: {e}")
                await self.client.close()
                logger.info(f"Reconnecting in {self.RETRY_DELAY} seconds...")
                await asyncio.sleep(self.RETRY_DELAY)
            except CancelledError:
                logger.info("Simulated client run cancelled, shutting down")
                await self.client.close()
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await self.client.close()
                raise

    async def _receive_loop(self, session: ClientProtocolSession):
        while True:
            frame = await self.client.read()
            if response_frame := session.handle_incoming_frame(frame):
                await self.client.write(response_frame)

    async def _send_loop(self, session: ClientProtocolSession):
        while True:
            await asyncio.sleep(1)
            for frame in session.get_periodic_frame_to_send():
                await self.client.write(frame)
