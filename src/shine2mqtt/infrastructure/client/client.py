import asyncio
from asyncio import CancelledError, IncompleteReadError

from shine2mqtt.infrastructure.client.transport import TCPTransport
from shine2mqtt.protocol.simulator.config import SimulatedClientConfig
from shine2mqtt.protocol.simulator.factory import ClientProtocolSessionFactory
from shine2mqtt.protocol.simulator.session import ClientProtocolSession
from shine2mqtt.util.logger import logger


class SimulatedClient:
    """Simulated Growatt datalogger client that connects to a server, announces itself, and periodically sends data frames."""

    RETRY_DELAY = 2

    def __init__(
        self,
        transport: TCPTransport,
        session_factory: ClientProtocolSessionFactory,
        config: SimulatedClientConfig,
    ):
        self.config = config
        self.transport = transport
        self.session_factory = session_factory

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
                logger.warning("Simulated client run cancelled, shutting down")
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
                    logger.info(
                        f"→ Sending {action.function_code.name} (0x{action.function_code.value:02x}) message"
                    )
                    await self.transport.write(frame)
