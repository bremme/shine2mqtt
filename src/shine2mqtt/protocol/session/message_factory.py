from shine2mqtt.protocol.frame.header.header import FunctionCode, MBAPHeader
from shine2mqtt.protocol.messages.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.messages.get_config.get_config import GrowattGetConfigRequestMessage
from shine2mqtt.protocol.messages.raw.raw import GrowattRawMessage
from shine2mqtt.protocol.messages.read_register.read_register import (
    GrowattReadRegistersRequestMessage,
)
from shine2mqtt.protocol.messages.set_config.set_config import GrowattSetConfigRequestMessage
from shine2mqtt.protocol.session.state import TransactionIdTracker


class MessageFactory:
    def __init__(self, protocol_id: int, unit_id: int, tracker: TransactionIdTracker):
        self._protocol_id = protocol_id
        self._unit_id = unit_id
        self._tracker = tracker

    def ack(self, header: MBAPHeader) -> GrowattAckMessage:
        return GrowattAckMessage(header=header, ack=True)

    def update_transaction_id(self, header: MBAPHeader) -> None:
        self._tracker.set_incoming_transaction_id(header)

    def get_config_request(
        self, datalogger_serial: str, register: int
    ) -> GrowattGetConfigRequestMessage:
        header = self._make_header(FunctionCode.GET_CONFIG)
        return GrowattGetConfigRequestMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register_start=register,
            register_end=register,
        )

    def set_config_request(
        self, datalogger_serial: str, register: int, value: str
    ) -> GrowattSetConfigRequestMessage:
        header = self._make_header(FunctionCode.SET_CONFIG)
        return GrowattSetConfigRequestMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register=register,
            value=value,
        )

    def read_registers_request(
        self, datalogger_serial: str, register_start: int, register_end: int
    ) -> GrowattReadRegistersRequestMessage:
        header = self._make_header(FunctionCode.READ_REGISTERS)
        return GrowattReadRegistersRequestMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register_start=register_start,
            register_end=register_end,
        )

    def raw_frame_request(
        self, datalogger_serial: str, function_code: int, payload: bytes
    ) -> GrowattRawMessage:
        fc = FunctionCode(function_code)
        header = MBAPHeader(
            transaction_id=self._tracker.get_next_transaction_id(fc),
            protocol_id=self._protocol_id,
            unit_id=self._unit_id,
            function_code=fc,
            length=0,
        )
        return GrowattRawMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            payload=payload,
        )

    def _make_header(self, function_code: FunctionCode) -> MBAPHeader:
        return MBAPHeader(
            transaction_id=self._tracker.get_next_transaction_id(function_code),
            protocol_id=self._protocol_id,
            unit_id=self._unit_id,
            function_code=function_code,
            length=0,
        )
