from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from shine2mqtt.domain.events.events import DomainEvent
from shine2mqtt.infrastructure.server.session import TCPSession
from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.messages.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.messages.announce.announce import GrowattAnnounceMessage
from shine2mqtt.protocol.messages.get_config.get_config import GrowattGetConfigResponseMessage
from shine2mqtt.protocol.session.base import BaseProtocolSession
from shine2mqtt.protocol.session.mapper import MessageEventMapper
from shine2mqtt.protocol.session.message_factory import MessageFactory
from shine2mqtt.protocol.session.state import ServerProtocolSessionState, TransactionIdTracker
from shine2mqtt.protocol.settings.constants import DATALOGGER_SW_VERSION_REGISTER
from shine2mqtt.util.logger import logger

if TYPE_CHECKING:
    from shine2mqtt.protocol.session.session import ProtocolSession


class ProtocolSessionInitializer(BaseProtocolSession):
    def __init__(
        self,
        encoder: FrameEncoder,
        decoder: FrameDecoder,
        mapper: MessageEventMapper,
        transport: TCPSession,
        domain_events: asyncio.Queue[DomainEvent],
    ):
        super().__init__(transport=transport, encoder=encoder, decoder=decoder)
        self.mapper = mapper
        self.domain_events = domain_events
        self.transaction_id_tracker = TransactionIdTracker()

    async def initialize(self) -> ProtocolSession:
        from shine2mqtt.protocol.session.session import ProtocolSession

        logger.info("Initializing protocol session, waiting for announce message...")
        announce = await self._wait_for_announce()

        factory = MessageFactory(
            protocol_id=announce.header.protocol_id,
            unit_id=announce.header.unit_id,
            tracker=self.transaction_id_tracker,
        )

        config = await self._request_datalogger_config(factory, announce.datalogger_serial)

        inverter = self.mapper.map_announce_message_to_inverter(announce)
        datalogger = self.mapper.map_config_sw_version_to_datalogger(
            config,
            protocol_id=announce.header.protocol_id,
            unit_id=announce.header.unit_id,
        )

        state = ServerProtocolSessionState(datalogger=datalogger, inverter=inverter)
        return ProtocolSession(
            transport=self.transport,
            state=state,
            factory=factory,
            encoder=self.encoder,
            decoder=self.decoder,
            domain_events=self.domain_events,
        )

    async def _wait_for_announce(self) -> GrowattAnnounceMessage:
        while True:
            match message := await self._read_message():
                case GrowattAnnounceMessage():
                    response = GrowattAckMessage(header=message.header, ack=True)
                    await self._write_message(response)
                    return message
                case _:
                    logger.warning(
                        f"Received unexpected message while waiting for announce: {message}"
                    )

    async def _request_datalogger_config(
        self, factory: MessageFactory, datalogger_serial: str
    ) -> GrowattGetConfigResponseMessage:
        message = factory.get_config_request(
            datalogger_serial=datalogger_serial,
            register=DATALOGGER_SW_VERSION_REGISTER,
        )

        await self._write_message(message)

        while True:
            match message := await self._read_message():
                case GrowattGetConfigResponseMessage() if (
                    message.register == DATALOGGER_SW_VERSION_REGISTER
                ):
                    logger.info("Received datalogger SW version config response")
                    return message
                case _:
                    logger.warning(
                        f"Received unexpected message while waiting for config response: {message}"
                    )
