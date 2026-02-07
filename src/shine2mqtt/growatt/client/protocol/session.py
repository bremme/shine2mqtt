from collections.abc import Iterator

from loguru import logger

from shine2mqtt.growatt.client.config import SimulatedClientConfig
from shine2mqtt.growatt.client.protocol.generator import DataGenerator
from shine2mqtt.growatt.client.protocol.state import ClientProtocolSessionState
from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.frame.capturer.sanitizer import DUMMY_DATALOGGER_SERIAL
from shine2mqtt.growatt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.growatt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.growatt.protocol.messages.ack import GrowattAckMessage
from shine2mqtt.growatt.protocol.messages.config import (
    GrowattGetConfigRequestMessage,
    GrowattSetConfigRequestMessage,
)
from shine2mqtt.growatt.protocol.messages.ping import GrowattPingMessage
from shine2mqtt.util.clock import ClockService, has_interval_elapsed


class ClientProtocolSession:
    def __init__(
        self,
        encoder: FrameEncoder,
        decoder: FrameDecoder,
        session_state: ClientProtocolSessionState,
        clock: ClockService,
        generator: DataGenerator,
        config: SimulatedClientConfig,
    ):
        self.encoder = encoder
        self.decoder = decoder
        self.session_state = session_state
        self.clock = clock
        self.generator = generator
        self.announce_interval = config.announce_interval
        self.data_interval = config.data_interval
        self.ping_interval = config.ping_interval

    def handle_incoming_frame(self, frame: bytes) -> bytes | None:
        message = self.decoder.decode(frame)

        function_code = message.header.function_code

        match message:
            case GrowattAckMessage() if function_code == FunctionCode.ANNOUNCE:
                logger.info("✓ Received ACK response for ANNOUNCE, datalogger is now announced")
                self.session_state.announce(message)
            case GrowattAckMessage() if function_code == FunctionCode.DATA:
                logger.info("✓ Received ACK response for DATA")
            case GrowattAckMessage() if function_code == FunctionCode.BUFFERED_DATA:
                logger.info("✓ Received ACK response for BUFFERED_DATA")
            case GrowattPingMessage():
                logger.info("✓ Received PING message response")
            case GrowattGetConfigRequestMessage():
                logger.info("✓ Received GET_CONFIG request message")
                return self._build_get_config_response_frame(message)
            case GrowattSetConfigRequestMessage():
                logger.info("✓ Received SET_CONFIG request")
                return self._build_ack_frame(message)
            case _:
                logger.warning(f"⚠ Unhandled message type: {type(message)}")

    def get_periodic_frame_to_send(self) -> Iterator[bytes]:
        if self._need_to_send_announce():
            frame = self._build_announce_frame()
            self.session_state.last_announce_time = self.clock.now()
            logger.info("→ Sending ANNOUNCE message")
            yield frame

        if self._need_to_send_data():
            frame = self._build_data_frame()
            self.session_state.last_data_time = self.clock.now()
            logger.info("→ Sending DATA message")
            yield frame

        if self._need_to_send_ping():
            frame = self._build_ping_frame()
            self.session_state.last_ping_time = self.clock.now()
            logger.info("→ Sending PING message")
            yield frame

    def _need_to_send_announce(self) -> bool:
        if self.session_state.is_announced():
            return False

        return has_interval_elapsed(
            now=self.clock.now(),
            last_time=self.session_state.last_announce_time,
            interval=self.announce_interval,
        )

    def _need_to_send_data(self) -> bool:
        if not self.session_state.is_announced():
            return False

        return has_interval_elapsed(
            now=self.clock.now(),
            last_time=self.session_state.last_data_time,
            interval=self.data_interval,
        )

    def _need_to_send_ping(self) -> bool:
        if not self.session_state.is_announced():
            return False

        return has_interval_elapsed(
            now=self.clock.now(),
            last_time=self.session_state.last_ping_time,
            interval=self.ping_interval,
        )

    def _build_announce_frame(self) -> bytes:
        transaction_id = self.session_state.get_transaction_id(FunctionCode.ANNOUNCE)
        return self.generator.generate_announce_frame(transaction_id=transaction_id)

    def _build_data_frame(self) -> bytes:
        transaction_id = self.session_state.get_transaction_id(FunctionCode.DATA)
        return self.generator.generate_data_frame(transaction_id=transaction_id)

    def _build_ping_frame(self) -> bytes:
        transaction_id = self.session_state.get_transaction_id(FunctionCode.PING)
        return self.generator.generate_ping_frame(transaction_id=transaction_id)

    def _build_get_config_response_frame(
        self, request_message: GrowattGetConfigRequestMessage
    ) -> bytes:
        return self.generator.generate_get_config_response_frame(
            transaction_id=request_message.header.transaction_id,
            register=request_message.register_start,
        )

    def _build_ack_frame(self, request_message: GrowattSetConfigRequestMessage) -> bytes:
        message = GrowattAckMessage(header=request_message.header, ack=True)
        return self.encoder.encode(message)


class ClientProtocolSessionFactory:
    def __init__(
        self,
        encoder: FrameEncoder,
        decoder: FrameDecoder,
        config: SimulatedClientConfig,
        clock: ClockService,
    ):
        self.encoder = encoder
        self.decoder = decoder
        self.config = config
        self.clock = clock
        self.generator = DataGenerator(self.encoder)

    def create(self) -> ClientProtocolSession:
        session_state = ClientProtocolSessionState(
            protocol_id=1, unit_id=1, datalogger_serial=DUMMY_DATALOGGER_SERIAL
        )

        return ClientProtocolSession(
            encoder=self.encoder,
            decoder=self.decoder,
            session_state=session_state,
            clock=self.clock,
            generator=self.generator,
            config=self.config,
        )
