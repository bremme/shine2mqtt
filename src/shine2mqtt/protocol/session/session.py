import asyncio

from shine2mqtt.domain.events.events import DomainEvent
from shine2mqtt.domain.interfaces.session import Session
from shine2mqtt.infrastructure.server.session import TCPSession
from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.messages.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.messages.announce.announce import GrowattAnnounceMessage
from shine2mqtt.protocol.messages.data.data import GrowattBufferedDataMessage, GrowattDataMessage
from shine2mqtt.protocol.messages.message import BaseMessage, DataloggerMessage
from shine2mqtt.protocol.messages.ping.message import GrowattPingMessage
from shine2mqtt.protocol.session.initializer import ProtocolSessionInitializer
from shine2mqtt.protocol.session.mapper import MessageEventMapper
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

    def create_initializer(self, transport: TCPSession) -> ProtocolSessionInitializer:
        mapper = MessageEventMapper()
        return ProtocolSessionInitializer(
            encoder=self.encoder,
            decoder=self.decoder,
            mapper=mapper,
            transport=transport,
        )

    def create(self, state: ServerProtocolSessionState, transport: TCPSession) -> ProtocolSession:
        return ProtocolSession(
            transport=transport,
            state=state,
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
        self.mapper = MessageEventMapper()
        self.state = state

    @property
    def datalogger(self):
        return self.state.datalogger

    @property
    def inverter(self):
        return self.state.inverter

    async def run(self):
        event = self.mapper.map_state_to_announce_event(self.state)
        self.domain_events.put_nowait(event)

        while True:
            message = await self._read_message()

            if message is None:
                continue

            if isinstance(message, DataloggerMessage):
                transaction_id = message.header.transaction_id
                datalogger_serial = message.datalogger_serial
                logger.info(
                    f"✓ Receive {message.header.function_code.name} ({message.header.function_code.value:#02x}) message, {transaction_id=}, {datalogger_serial=}"
                )

            self.publish_domain_event(message)

            # respond to periodic datalogger messages
            if self.is_periodic_message(message):
                await self.respond_to_periodic_message(message)
            elif self.is_response_message(message):
                await self.handle_response_message(message)

        # complete datalogger response futures

    async def close(self):
        logger.info("Closing protocol session")
        await self.transport.close()

    async def _read_message(self) -> BaseMessage | None:
        frame = await self.transport.read_frame()

        try:
            return self.decoder.decode(frame)
        except Exception as e:
            logger.error(f"Failed to decode incoming frame {frame}: {e}")

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

    def publish_domain_event(self, message: BaseMessage) -> None:
        match message:
            case GrowattDataMessage() | GrowattBufferedDataMessage():
                event = self.mapper.map_data_message_to_inverter_state_updated_event(message)
            case _:
                return

        self.domain_events.put_nowait(event)

    async def respond_to_periodic_message(self, message: BaseMessage) -> None:
        self.state.set_incoming_transaction_id(message.header)

        match message:
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
