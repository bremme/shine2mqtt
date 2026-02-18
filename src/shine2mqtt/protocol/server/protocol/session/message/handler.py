from shine2mqtt.protocol.protocol.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.protocol.announce.announce import GrowattAnnounceMessage
from shine2mqtt.protocol.protocol.base.message import BaseMessage
from shine2mqtt.protocol.protocol.constants import DATALOGGER_SW_VERSION_REGISTER, FunctionCode
from shine2mqtt.protocol.protocol.data.data import (
    GrowattBufferedDataMessage,
    GrowattDataMessage,
)
from shine2mqtt.protocol.protocol.get_config.get_config import (
    GrowattGetConfigRequestMessage,
)
from shine2mqtt.protocol.protocol.header.header import MBAPHeader
from shine2mqtt.protocol.protocol.ping.message import GrowattPingMessage
from shine2mqtt.protocol.server.protocol.session.state import ServerProtocolSessionState
from shine2mqtt.util.logger import logger


class MessageHandler:
    _GET_CONFIG_REGISTER_START = 0
    _GET_CONFIG_REGISTER_END = 61

    def __init__(self, session_state: ServerProtocolSessionState):
        self.session_state = session_state

    def build_announce_response(self, message: GrowattAnnounceMessage) -> list[BaseMessage]:
        self._handle_message_default_actions(message)

        response_messages = []

        response_messages.append(GrowattAckMessage(header=message.header, ack=True))

        if not self.session_state.is_announced():
            self.session_state.announce(message)
            # get software version first to enable device discovery
            # TODO this should be configurable
            # FIXME perhaps gettign the config should be indepdent of the announce message
            response_messages.append(
                self._build_get_config_request_message(
                    register_start=DATALOGGER_SW_VERSION_REGISTER,
                    register_end=DATALOGGER_SW_VERSION_REGISTER,
                )
            )
            response_messages.append(
                self._build_get_config_request_message(
                    # register_start=self._GET_CONFIG_REGISTER_START,
                    # register_end=self._GET_CONFIG_REGISTER_END,
                    register_start=0,
                    register_end=5,
                )
            )

        return response_messages

    def build_data_response(self, message: GrowattDataMessage) -> list[BaseMessage]:
        self._handle_message_default_actions(message)
        return [GrowattAckMessage(header=message.header, ack=True)]

    def build_buffered_data_response(
        self, message: GrowattBufferedDataMessage
    ) -> list[BaseMessage]:
        return self.build_data_response(message)

    def build_ping_response(self, message: GrowattPingMessage) -> list[BaseMessage]:
        self._handle_message_default_actions(message)
        return [message]

    def _handle_message_default_actions(self, message: BaseMessage) -> None:
        logger.debug(f"Message content: {message}")

        self.session_state.set_incoming_transaction_id(message.header)

    def _build_get_config_request_message(self, register_start, register_end=None):
        if register_end is None:
            register_end = register_start

        function_code = FunctionCode.GET_CONFIG
        transaction_id = self.session_state.get_next_transaction_id(function_code)

        header = MBAPHeader(
            transaction_id=transaction_id,
            protocol_id=self.session_state.protocol_id,
            length=0,
            unit_id=self.session_state.unit_id,
            function_code=function_code,
        )

        return GrowattGetConfigRequestMessage(
            header, self.session_state.datalogger_serial, register_start, register_end
        )
