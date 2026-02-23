import asyncio
from datetime import datetime

from shine2mqtt.domain.events.events import DomainEvent
from shine2mqtt.infrastructure.server.session import TCPSession
from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.messages.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.messages.announce.announce import GrowattAnnounceMessage
from shine2mqtt.protocol.messages.get_config.get_config import GrowattGetConfigResponseMessage
from shine2mqtt.protocol.messages.ping.message import GrowattPingMessage
from shine2mqtt.protocol.messages.set_config.set_config import GrowattSetConfigResponseMessage
from shine2mqtt.protocol.session.base import BaseProtocolSession
from shine2mqtt.protocol.session.mapper import MessageEventMapper
from shine2mqtt.protocol.session.message_factory import MessageFactory
from shine2mqtt.protocol.session.session import ProtocolSession
from shine2mqtt.protocol.session.state import ServerProtocolSessionState, TransactionIdTracker
from shine2mqtt.protocol.settings.constants import (
    DATALOGGER_IP_ADDRESS_REGISTER,
    DATALOGGER_MAC_ADDRESS_REGISTER,
    DATALOGGER_SW_VERSION_REGISTER,
    DATALOGGER_SYSTEM_TIME_REGISTER,
)
from shine2mqtt.util.logger import logger


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
        logger.info("Initializing protocol session, waiting for announce message...")
        announce = await self._wait_for_announce()

        factory = MessageFactory(
            protocol_id=announce.header.protocol_id,
            unit_id=announce.header.unit_id,
            tracker=self.transaction_id_tracker,
        )

        await self._sync_datalogger_system_time(factory, announce)

        sw_version = await self._request_datalogger_config(
            factory, announce.datalogger_serial, register=DATALOGGER_SW_VERSION_REGISTER
        )
        ip_address = await self._request_datalogger_config(
            factory, announce.datalogger_serial, register=DATALOGGER_IP_ADDRESS_REGISTER
        )
        mac_address = await self._request_datalogger_config(
            factory, announce.datalogger_serial, register=DATALOGGER_MAC_ADDRESS_REGISTER
        )

        inverter = self.mapper.map_announce_message_to_inverter(announce)
        datalogger = self.mapper.map_config_to_datalogger(
            datalogger_serial=announce.datalogger_serial,
            ip_address=ip_address,
            mac_address=mac_address,
            sw_version=sw_version,
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
                case GrowattPingMessage():
                    await self._write_message(message)
                case _:
                    logger.warning(
                        f"Received unexpected message while waiting for announce: {type(message).__name__}"
                    )

    async def _sync_datalogger_system_time(
        self, factory: MessageFactory, announce: GrowattAnnounceMessage
    ) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await self._write_datalogger_config(
            factory=factory,
            datalogger_serial=announce.datalogger_serial,
            register=DATALOGGER_SYSTEM_TIME_REGISTER,
            value=current_time,
        )

    async def _write_datalogger_config(
        self, factory: MessageFactory, datalogger_serial: str, register: int, value: str
    ) -> str:
        message = factory.set_config_request(
            datalogger_serial=datalogger_serial,
            register=register,
            value=value,
        )

        await self._write_message(message)

        while True:
            match message := await self._read_message():
                case GrowattSetConfigResponseMessage() if message.register == register:
                    return value
                case GrowattPingMessage():
                    await self._write_message(message)
                case _:
                    logger.warning(
                        f"Received unexpected message while waiting for set config response: {type(message).__name__}"
                    )

    async def _request_datalogger_config(
        self, factory: MessageFactory, datalogger_serial: str, register: int
    ) -> str:
        message = factory.get_config_request(
            datalogger_serial=datalogger_serial,
            register=register,
        )

        await self._write_message(message)

        while True:
            match message := await self._read_message():
                case GrowattGetConfigResponseMessage() if message.register == register:
                    return message.value
                case GrowattPingMessage():
                    await self._write_message(message)
                case _:
                    logger.warning(
                        f"Received unexpected message while waiting for get config response: {type(message).__name__}"
                    )
