from shine2mqtt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.protocol.simulator.config import SimulatedClientConfig
from shine2mqtt.protocol.simulator.generator import FrameGenerator
from shine2mqtt.protocol.simulator.handler import ClientMessageHandler
from shine2mqtt.protocol.simulator.session import ClientProtocolSession, SendIntervals
from shine2mqtt.protocol.simulator.state import ClientProtocolSessionState
from shine2mqtt.util.clock import ClockService
from shine2mqtt.util.strings import generate_random_uppercase_string


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
        self._datalogger_serial = generate_random_uppercase_string(10)

    def create(self) -> ClientProtocolSession:
        datalogger_serial = self._datalogger_serial
        session_state = ClientProtocolSessionState(
            protocol_id=1, unit_id=1, datalogger_serial=datalogger_serial
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
