import asyncio

from shine2mqtt.domain.events.events import DomainEvent
from shine2mqtt.infrastructure.server.session import TCPSession
from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.session.initializer import ProtocolSessionInitializer
from shine2mqtt.protocol.session.mapper import MessageEventMapper
from shine2mqtt.protocol.session.session import ProtocolSession


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

    async def create(self, transport: TCPSession) -> ProtocolSession:
        mapper = MessageEventMapper()
        initializer = ProtocolSessionInitializer(
            encoder=self.encoder,
            decoder=self.decoder,
            mapper=mapper,
            transport=transport,
            domain_events=self.domain_events,
        )
        return await initializer.initialize()
