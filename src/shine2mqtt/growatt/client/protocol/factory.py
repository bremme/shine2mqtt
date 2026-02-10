from shine2mqtt.growatt.client.config import SimulatedClientConfig
from shine2mqtt.growatt.client.protocol.generator import FrameGenerator
from shine2mqtt.growatt.client.protocol.handler import ClientMessageHandler
from shine2mqtt.growatt.client.protocol.session import ClientProtocolSession, SendIntervals
from shine2mqtt.growatt.client.protocol.state import ClientProtocolSessionState
from shine2mqtt.growatt.protocol.frame.capturer.sanitizer import DUMMY_DATALOGGER_SERIAL
from shine2mqtt.growatt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.util.clock import ClockService


class ClientProtocolSessionFactory:
    def __init__(
        self,
        decoder: FrameDecoder,
        config: SimulatedClientConfig,
        clock: ClockService,
        generator: FrameGenerator,
        message_handler: ClientMessageHandler,
    ):
        self.decoder = decoder
        self.config = config
        self.clock = clock
        self.generator = generator
        self.message_handler = message_handler

    def create(self) -> ClientProtocolSession:
        session_state = ClientProtocolSessionState(
            protocol_id=1, unit_id=1, datalogger_serial=DUMMY_DATALOGGER_SERIAL
        )

        self.message_handler.set_announce_callback(session_state.announce)

        send_intervals = SendIntervals(
            announce=self.config.announce_interval,
            data=self.config.data_interval,
            ping=self.config.ping_interval,
        )

        return ClientProtocolSession(
            decoder=self.decoder,
            session_state=session_state,
            clock=self.clock,
            generator=self.generator,
            message_handler=self.message_handler,
            send_intervals=send_intervals,
        )
