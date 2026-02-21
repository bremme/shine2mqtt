import asyncio

from shine2mqtt.domain.events.events import DomainEvent
from shine2mqtt.domain.interfaces.session import Session
from shine2mqtt.infrastructure.server.session import TCPSession
from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.messages.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.messages.announce.announce import GrowattAnnounceMessage
from shine2mqtt.protocol.messages.data.data import GrowattBufferedDataMessage, GrowattDataMessage
from shine2mqtt.protocol.messages.message import BaseMessage
from shine2mqtt.protocol.messages.ping.message import GrowattPingMessage
from shine2mqtt.protocol.session.base import BaseProtocolSession
from shine2mqtt.protocol.session.mapper import MessageEventMapper
from shine2mqtt.protocol.session.state import ServerProtocolSessionState
from shine2mqtt.util.logger import logger


class ProtocolSession(BaseProtocolSession, Session):
    def __init__(
        self,
        transport: TCPSession,
        state: ServerProtocolSessionState,
        encoder: FrameEncoder,
        decoder: FrameDecoder,
        domain_events: asyncio.Queue[DomainEvent],
    ):
        super().__init__(transport=transport, encoder=encoder, decoder=decoder)
        self.domain_events = domain_events
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

        await self._write_message(response)

    async def handle_response_message(self, message: BaseMessage) -> None:
        logger.debug(f"Received response message: {message}")
