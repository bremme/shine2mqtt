from shine2mqtt.protocol.frame.header.header import FunctionCode, MBAPHeader
from shine2mqtt.protocol.messages.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.messages.announce.announce import GrowattAnnounceMessage
from shine2mqtt.protocol.messages.get_config.get_config import (
    GrowattGetConfigRequestMessage,
    GrowattGetConfigResponseMessage,
)
from shine2mqtt.protocol.session.base import BaseProtocolSession
from shine2mqtt.protocol.session.state import ServerProtocolSessionState, TransactionIdTracker
from shine2mqtt.protocol.settings.constants import DATALOGGER_SW_VERSION_REGISTER
from shine2mqtt.util.logger import logger


class ProtocolSessionInitializer(BaseProtocolSession):
    def __init__(self, encoder, decoder, mapper, transport):
        super().__init__(transport=transport, encoder=encoder, decoder=decoder)
        self.mapper = mapper
        self.transaction_id_tracker = TransactionIdTracker()

    async def initialize(self) -> ServerProtocolSessionState:
        logger.info("Initializing protocol session, waiting for announce message...")
        announce = await self._wait_for_announce()
        config = await self._request_datalogger_config(
            protocol_id=announce.header.protocol_id,
            unit_id=announce.header.unit_id,
            datalogger_serial=announce.datalogger_serial,
        )

        inverter = self.mapper.map_announce_message_to_inverter(announce)
        datalogger = self.mapper.map_config_sw_version_to_datalogger(config)

        return ServerProtocolSessionState(
            protocol_id=announce.header.protocol_id,
            unit_id=announce.header.unit_id,
            datalogger=datalogger,
            inverter=inverter,
            transaction_id_tracker=self.transaction_id_tracker,
        )

    async def _wait_for_announce(self) -> GrowattAnnounceMessage:
        while True:
            match message := await self._read_message():
                case GrowattAnnounceMessage():
                    transaction_id = message.header.transaction_id
                    datalogger_serial = message.datalogger_serial
                    logger.info(
                        f"✓ ANNOUNCE (0x03) message, received and acknowledged {transaction_id=}, {datalogger_serial=}"
                    )
                    response = GrowattAckMessage(header=message.header, ack=True)
                    await self._write_message(response)
                    return message
                case _:
                    logger.warning(
                        f"Received unexpected message while waiting for announce: {message}"
                    )

    async def _request_datalogger_config(
        self, protocol_id, unit_id, datalogger_serial
    ) -> GrowattGetConfigResponseMessage:
        function_code = FunctionCode.GET_CONFIG
        transaction_id = self.transaction_id_tracker.get_next_transaction_id(function_code)

        header = MBAPHeader(
            transaction_id=transaction_id,
            protocol_id=protocol_id,
            length=0,
            unit_id=unit_id,
            function_code=function_code,
        )
        message = GrowattGetConfigRequestMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register_start=DATALOGGER_SW_VERSION_REGISTER,
            register_end=DATALOGGER_SW_VERSION_REGISTER,
        )

        logger.info(f"→ Sending GET_CONFIG request for datalogger SW version, {transaction_id=}")

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
