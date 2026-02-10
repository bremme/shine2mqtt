from loguru import logger

from shine2mqtt.growatt.protocol.constants import DATALOGGER_SW_VERSION_REGISTER, FunctionCode
from shine2mqtt.growatt.protocol.messages import (
    BaseMessage,
    GrowattAckMessage,
    GrowattAnnounceMessage,
    GrowattBufferedDataMessage,
    GrowattDataMessage,
    GrowattGetConfigRequestMessage,
    GrowattGetConfigResponseMessage,
    GrowattPingMessage,
    MBAPHeader,
)
from shine2mqtt.growatt.server.protocol.session.state import ServerProtocolSessionState


class MessageHandler:
    _GET_CONFIG_REGISTER_START = 0
    _GET_CONFIG_REGISTER_END = 61

    def __init__(self, session_state: ServerProtocolSessionState):
        self.session_state = session_state

    def handle_message(self, message: BaseMessage) -> list[BaseMessage]:
        logger.info(
            f"Processing incoming {message.header.function_code.name} ({message.header.function_code.value:#02x}) message."
        )
        logger.debug(f"Message content: {message}")

        self.session_state.set_incoming_transaction_id(message.header)

        match message:
            case GrowattPingMessage():
                response_messages = self._handle_ping_request(message)
            case GrowattAnnounceMessage():
                response_messages = self._handle_announce_request(message)
            case GrowattDataMessage() | GrowattBufferedDataMessage():
                response_messages = self._handle_data_request(message)
            case GrowattAckMessage():
                response_messages = self._handle_set_config_response()
            case GrowattGetConfigResponseMessage():
                response_messages = self._handle_get_config_response(message)
            case _:
                logger.error(f"No handler for message type: {type(message)}")
                response_messages: list[BaseMessage] = []

        return response_messages

    def _handle_ping_request(self, message: GrowattPingMessage) -> list[BaseMessage]:
        return [message]

    def _handle_announce_request(self, message: GrowattAnnounceMessage) -> list[BaseMessage]:
        response_messages = []

        response_messages.append(GrowattAckMessage(header=message.header, ack=True))

        if not self.session_state.is_announced():
            self.session_state.announce(message)
            # get software version first to enable device discovery
            # TODO this should be configurable
            response_messages.append(
                self._build_get_config_request_message(
                    register_start=DATALOGGER_SW_VERSION_REGISTER,
                    register_end=DATALOGGER_SW_VERSION_REGISTER,
                )
            )
            response_messages.append(
                self._build_get_config_request_message(
                    register_start=self._GET_CONFIG_REGISTER_START,
                    register_end=self._GET_CONFIG_REGISTER_END,
                )
            )

        return response_messages

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

    def _handle_data_request(self, message: GrowattDataMessage) -> list[BaseMessage]:
        return [GrowattAckMessage(header=message.header, ack=True)]

    def _handle_buffered_data_request(
        self, message: GrowattBufferedDataMessage
    ) -> list[BaseMessage]:
        return [GrowattAckMessage(header=message.header, ack=True)]

    def _handle_set_config_response(self) -> list[BaseMessage]:
        # this just ack the set config command
        return []

    def _handle_get_config_response(
        self, message: GrowattGetConfigResponseMessage
    ) -> list[BaseMessage]:
        logger.info(
            f"Received config register={message.register} name='{message.name}', value='{message.value}'"
        )
        return []
