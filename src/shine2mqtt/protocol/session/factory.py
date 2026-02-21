import asyncio

from shine2mqtt.domain.events.events import DomainEvent
from shine2mqtt.infrastructure.server.session import TCPSession
from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.session.initializer import ProtocolSessionInitializer
from shine2mqtt.protocol.session.mapper import MessageEventMapper


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
            domain_events=self.domain_events,
        )
