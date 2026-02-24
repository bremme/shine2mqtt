import asyncio
from typing import Any, override

from shine2mqtt.domain.events.events import DomainEvent
from shine2mqtt.domain.interfaces.session import Session
from shine2mqtt.domain.models.config import ConfigResult
from shine2mqtt.infrastructure.server.session import TCPSession
from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.messages.announce.announce import GrowattAnnounceMessage
from shine2mqtt.protocol.messages.data.data import GrowattBufferedDataMessage, GrowattDataMessage
from shine2mqtt.protocol.messages.message import BaseMessage
from shine2mqtt.protocol.messages.ping.message import GrowattPingMessage
from shine2mqtt.protocol.session.base import BaseProtocolSession
from shine2mqtt.protocol.session.mapper import MessageEventMapper
from shine2mqtt.protocol.session.message_factory import MessageFactory
from shine2mqtt.protocol.session.response_tracker import PendingResponseTracker
from shine2mqtt.protocol.session.state import ServerProtocolSessionState
from shine2mqtt.util.logger import logger


class ProtocolSession(BaseProtocolSession, Session):
    def __init__(
        self,
        transport: TCPSession,
        state: ServerProtocolSessionState,
        factory: MessageFactory,
        encoder: FrameEncoder,
        decoder: FrameDecoder,
        domain_events: asyncio.Queue[DomainEvent],
    ):
        super().__init__(transport=transport, encoder=encoder, decoder=decoder)
        self._domain_events = domain_events
        self._mapper = MessageEventMapper()
        self._state = state
        self._factory = factory
        self._tracker = PendingResponseTracker()

    @property
    @override
    def datalogger(self):
        return self._state.datalogger

    @property
    def inverter(self):
        return self._state.inverter

    async def run(self):
        event = self._mapper.map_state_to_announce_event(self._state)
        self._domain_events.put_nowait(event)

        while True:
            message = await self._read_message()

            if message is None:
                continue

            self._publish_domain_event(message)

            if self._is_periodic_message(message):
                await self._respond_to_periodic_message(message)
            else:
                self._tracker.resolve(message)

    async def close(self):
        logger.info("Closing protocol session")
        await self.transport.close()

    @override
    async def get_config(self, register: int) -> ConfigResult:
        request = self._factory.get_config_request(self.datalogger.serial, register)
        return await self._resolve_request(request)

    @override
    async def set_config(self, register: int, value: str) -> bool:
        request = self._factory.set_config_request(self.datalogger.serial, register, value)
        return await self._resolve_request(request)

    @override
    async def read_registers(self, register_start: int, register_end: int) -> dict[int, int]:
        request = self._factory.read_registers_request(
            self.datalogger.serial, register_start, register_end
        )
        return await self._resolve_request(request)

    @override
    async def write_single_register(self, register: int, value: int) -> bool:
        request = self._factory.write_single_register_request(
            self.datalogger.serial, register, value
        )
        return await self._resolve_request(request)

    @override
    async def write_multiple_registers(
        self, register_start: int, register_end: int, values: bytes
    ) -> bool:
        request = self._factory.write_multiple_registers_request(
            self.datalogger.serial, register_start, register_end, values
        )
        return await self._resolve_request(request)

    @override
    async def send_raw_frame(self, function_code: int, payload: bytes) -> bytes:
        request = self._factory.raw_frame_request(self.datalogger.serial, function_code, payload)
        return await self._resolve_request(request)

    async def _resolve_request(self, request: BaseMessage) -> Any:
        future_response = self._tracker.track(request)
        await self._write_message(request)
        return await future_response

    def _is_periodic_message(self, message: BaseMessage) -> bool:
        return isinstance(
            message,
            (
                GrowattAnnounceMessage,
                GrowattPingMessage,
                GrowattDataMessage,
                GrowattBufferedDataMessage,
            ),
        )

    async def _respond_to_periodic_message(self, message: BaseMessage) -> None:
        self._factory.update_transaction_id(message.header)

        match message:
            case GrowattDataMessage() | GrowattBufferedDataMessage():
                response = self._factory.ack(message.header)
            case GrowattPingMessage():
                response = message
            case _:
                logger.warning(f"Received unknown periodic message type: {type(message)}")
                return

        await self._write_message(response)

    def _publish_domain_event(self, message: BaseMessage) -> None:
        match message:
            case GrowattDataMessage() | GrowattBufferedDataMessage():
                event = self._mapper.map_data_message_to_inverter_state_updated_event(message)
            case _:
                return

        self._domain_events.put_nowait(event)
