import asyncio
from asyncio import CancelledError, IncompleteReadError

from loguru import logger

from shine2mqtt.growatt.client.config import SimulatedClientConfig
from shine2mqtt.growatt.client.protocol.factory import ClientProtocolSessionFactory
from shine2mqtt.growatt.client.protocol.generator import FrameGenerator
from shine2mqtt.growatt.client.protocol.handler import ClientMessageHandler
from shine2mqtt.growatt.client.protocol.session import (
    ClientProtocolSession,
)
from shine2mqtt.growatt.client.transport import TCPTransport
from shine2mqtt.growatt.protocol.frame.factory import FrameFactory
from shine2mqtt.util.clock import MonotonicClockService


class SimulatedClient:
    """Simulated Growatt datalogger client that connects to a server, announces itself, and periodically sends data frames."""

    RETRY_DELAY = 2

    def __init__(self, config: SimulatedClientConfig):
        self.config = config
        self.transport = TCPTransport()

        encoder = FrameFactory.encoder()
        decoder = FrameFactory.client_decoder()
        clock = MonotonicClockService()

        generator = FrameGenerator(encoder=encoder)
        message_handler = ClientMessageHandler(generator=generator)

        self.session_factory = ClientProtocolSessionFactory(
            decoder=decoder,
            config=config,
            clock=clock,
            generator=generator,
            message_handler=message_handler,
        )

    async def run(self):
        while True:
            try:
                await self.transport.connect(self.config.server_host, self.config.server_port)

                logger.info("Starting protocol session")
                session = self.session_factory.create()

                await asyncio.gather(
                    self._receive_loop(session),
                    self._send_loop(session),
                )
            except (IncompleteReadError, ConnectionRefusedError) as e:
                logger.warning(f"Connection lost or failed: {e}")
                await self.transport.close()
                logger.info(f"Reconnecting in {self.RETRY_DELAY} seconds...")
                await asyncio.sleep(self.RETRY_DELAY)
            except CancelledError:
                logger.info("Simulated client run cancelled, shutting down")
                await self.transport.close()
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await self.transport.close()
                raise

    async def _receive_loop(self, session: ClientProtocolSession):
        while True:
            frame = await self.transport.read()
            if response_frame := session.handle_incoming_frame(frame):
                await self.transport.write(response_frame)

    async def _send_loop(self, session: ClientProtocolSession):
        while True:
            await asyncio.sleep(1)

            for action in session.get_pending_actions():
                if frame := session.get_send_message_frame(action):
                    logger.info(f"→ Sending {action.function_code.value} message")
                    await self.transport.write(frame)
