from dataclasses import dataclass

from shine2mqtt.protocol.client.protocol.generator import FrameGenerator
from shine2mqtt.protocol.client.protocol.handler import ClientMessageHandler
from shine2mqtt.protocol.client.protocol.state import ClientProtocolSessionState
from shine2mqtt.protocol.protocol.constants import FunctionCode
from shine2mqtt.protocol.protocol.frame.decoder import FrameDecoder
from shine2mqtt.util.clock import ClockService, has_interval_elapsed
from shine2mqtt.util.logger import logger


@dataclass
class SendMessageAction:
    function_code: FunctionCode


@dataclass
class SendIntervals:
    announce: int
    data: int
    ping: int


class ClientProtocolSession:
    def __init__(
        self,
        decoder: FrameDecoder,
        session_state: ClientProtocolSessionState,
        clock: ClockService,
        generator: FrameGenerator,
        message_handler: ClientMessageHandler,
        send_intervals: SendIntervals,
    ):
        self.decoder = decoder
        self.session_state = session_state
        self.clock = clock
        self.generator = generator
        self.message_handler = message_handler
        self.intervals = send_intervals

    def handle_incoming_frame(self, frame: bytes) -> bytes | None:
        message = self.decoder.decode(frame)

        return self.message_handler.handle_message(message)

    def get_pending_actions(self) -> list[SendMessageAction]:
        actions = []

        if self._need_to_send_announce():
            actions.append(SendMessageAction(function_code=FunctionCode.ANNOUNCE))

        if self._need_to_send_data():
            actions.append(SendMessageAction(function_code=FunctionCode.DATA))

        if self._need_to_send_ping():
            actions.append(SendMessageAction(function_code=FunctionCode.PING))

        return actions

    def get_send_message_frame(self, action: SendMessageAction) -> bytes | None:
        match action.function_code:
            case FunctionCode.ANNOUNCE | FunctionCode.DATA | FunctionCode.PING:
                return self._generate_frame(function_code=action.function_code)

            case _:
                logger.warning(
                    f"⚠ No frame generation logic for function code {action.function_code}"
                )
                return None

    def _generate_frame(self, function_code: FunctionCode) -> bytes:
        self.session_state.update_last_send(function_code, self.clock.now())
        transaction_id = self.session_state.get_next_transaction_id(function_code)
        return self.generator.generate_frame(
            transaction_id=transaction_id, function_code=function_code
        )

    def _need_to_send_announce(self) -> bool:
        if self.session_state.is_announced():
            return False

        return has_interval_elapsed(
            now=self.clock.now(),
            last_time=self.session_state.get_last_send(FunctionCode.ANNOUNCE),
            interval=self.intervals.announce,
        )

    def _need_to_send_data(self) -> bool:
        if not self.session_state.is_announced():
            return False

        return has_interval_elapsed(
            now=self.clock.now(),
            last_time=self.session_state.get_last_send(FunctionCode.DATA),
            interval=self.intervals.data,
        )

    def _need_to_send_ping(self) -> bool:
        if not self.session_state.is_announced():
            return False

        return has_interval_elapsed(
            now=self.clock.now(),
            last_time=self.session_state.get_last_send(FunctionCode.PING),
            interval=self.intervals.ping,
        )
