import asyncio

from shine2mqtt.domain.events.base import DomainEvent
from shine2mqtt.domain.interfaces.session import Session
from shine2mqtt.domain.models.datalogger import DataLogger
from shine2mqtt.infrastructure.server.session import TCPSession
from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.messages.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.messages.announce.announce import GrowattAnnounceMessage
from shine2mqtt.protocol.messages.data.data import GrowattBufferedDataMessage, GrowattDataMessage
from shine2mqtt.protocol.messages.message import BaseMessage, DataloggerMessage
from shine2mqtt.protocol.messages.ping.message import GrowattPingMessage
from shine2mqtt.protocol.session.state import ServerProtocolSessionState
from shine2mqtt.util.logger import logger


class ProtocolSessionFactory:
    def __init__(
        self,
        encoder: FrameEncoder,
        decoder: FrameDecoder,
        domain_events: asyncio.Queue[DomainEvent],
    ):
        self.encoder = encoder
        self.decoder = decoder
        self.domain_events = domain_events

    def create(self, transport: TCPSession) -> ProtocolSession:
        session_state = ServerProtocolSessionState()

        return ProtocolSession(
            transport=transport,
            state=session_state,
            decoder=self.decoder,
            encoder=self.encoder,
            domain_events=self.domain_events,
        )


class ProtocolSession(Session):
    def __init__(
        self,
        transport: TCPSession,
        state: ServerProtocolSessionState,
        encoder: FrameEncoder,
        decoder: FrameDecoder,
        domain_events: asyncio.Queue[DomainEvent],
    ):
        self.transport = transport
        self.domain_events = domain_events
        self.decoder = decoder
        self.encoder = encoder
        self.state = state

    @property
    def datalogger(self):
        if self.state.is_announced() is False:
            return None
        return DataLogger(
            serial=self.state.datalogger_serial,
        )

    @property
    def datalogger_serial(self) -> str:
        return self.state.datalogger_serial

    async def run(self):
        while True:
            frame = await self.transport.read_frame()

            try:
                message: BaseMessage = self.decoder.decode(frame)
            except Exception as e:
                logger.error(f"Failed to decode incoming frame {frame}: {e}")
                return

            transaction_id = message.header.transaction_id
            if isinstance(message, DataloggerMessage):
                datalogger_serial = message.datalogger_serial

                logger.info(
                    f"✓ Receive {message.header.function_code.name} ({message.header.function_code.value:#02x}) message, {transaction_id=}, {datalogger_serial=}"
                )

            # publish domain event
            # await self.event_queue.put_nowait(event)

            # respond to periodic datalogger messages
            if self.is_periodic_message(message):
                await self.handle_periodic_message(message)
            elif self.is_response_message(message):
                await self.handle_response_message(message)

        # complete datalogger response futures

    async def close(self):
        logger.info("Closing protocol session")
        await self.transport.close()

    def is_periodic_message(self, message: BaseMessage) -> bool:
        return isinstance(
            message,
            (
                GrowattAnnounceMessage,
                GrowattPingMessage,
                GrowattDataMessage,
                GrowattBufferedDataMessage,
            ),
        )

    def is_response_message(self, message: BaseMessage) -> bool:
        return not self.is_periodic_message(message)

    async def handle_periodic_message(self, message: BaseMessage) -> None:
        self.state.set_incoming_transaction_id(message.header)

        match message:
            case GrowattAnnounceMessage():
                self.state.announce(message)
                response = GrowattAckMessage(header=message.header, ack=True)
            case GrowattDataMessage() | GrowattBufferedDataMessage():
                response = GrowattAckMessage(header=message.header, ack=True)
            case GrowattPingMessage():
                response = message
            case _:
                logger.warning(f"Received unknown periodic message type: {type(message)}")
                return

        transaction_id = response.header.transaction_id
        logger.info(
            f"→ Enqueue {response.header.function_code.name} ({response.header.function_code.value:#02x}) response, {transaction_id=}"
        )

        response_frame = self.encoder.encode(response)

        await self.transport.write_frame(response_frame)

    async def handle_response_message(self, message: BaseMessage) -> None:
        logger.debug(f"Received response message: {message}")
