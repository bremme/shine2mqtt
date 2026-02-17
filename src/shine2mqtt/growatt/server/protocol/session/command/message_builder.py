from asyncio import Future

from shine2mqtt.growatt.protocol.config import ConfigRegistry
from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.get_config.get_config import (
    GrowattGetConfigRequestMessage,
)
from shine2mqtt.growatt.protocol.header.header import MBAPHeader
from shine2mqtt.growatt.protocol.raw.raw import GrowattRawMessage
from shine2mqtt.growatt.protocol.read_register.read_register import (
    GrowattReadRegistersRequestMessage,
)
from shine2mqtt.growatt.protocol.set_config.set_config import (
    GrowattSetConfigRequestMessage,
)
from shine2mqtt.growatt.server.protocol.session.command.command import (
    RawFrameCommand,
    ReadRegistersCommand,
)
from shine2mqtt.growatt.server.protocol.session.state import ServerProtocolSessionState


class CommandMessageBuilder:
    def __init__(self, session_state: ServerProtocolSessionState, config_registry: ConfigRegistry):
        self.session_state = session_state
        self.command_futures: dict[tuple[FunctionCode, int], Future] = {}
        self.config_registry = config_registry

    def build_get_config_message_by_name(self, register_name: str):
        register_start = self.config_registry.get_register_by_name(register_name)
        return self.build_get_config_message(register_start=register_start)

    def build_get_config_message(self, register_start, register_end=None):
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

    def build_set_config_message(self, register, value):
        function_code = FunctionCode.SET_CONFIG
        transaction_id = self.session_state.get_next_transaction_id(function_code)

        header = MBAPHeader(
            transaction_id=transaction_id,
            protocol_id=self.session_state.protocol_id,
            length=0,
            unit_id=self.session_state.unit_id,
            function_code=function_code,
        )

        return GrowattSetConfigRequestMessage(
            header, self.session_state.datalogger_serial, register, value
        )

    def build_raw_frame_message(self, command: RawFrameCommand) -> GrowattRawMessage:
        header = MBAPHeader(
            transaction_id=self.session_state.get_next_transaction_id(
                FunctionCode(command.function_code)
            ),
            protocol_id=command.protocol_id,
            length=0,
            unit_id=self.session_state.unit_id,
            function_code=FunctionCode(command.function_code),
        )

        return GrowattRawMessage(
            header=header,
            datalogger_serial=self.session_state.datalogger_serial,
            payload=command.payload,
        )

    def build_read_registers_message(
        self, command: ReadRegistersCommand
    ) -> GrowattReadRegistersRequestMessage:
        header = MBAPHeader(
            transaction_id=self.session_state.get_next_transaction_id(FunctionCode.READ_REGISTERS),
            protocol_id=self.session_state.protocol_id,
            length=0,
            unit_id=self.session_state.unit_id,
            function_code=FunctionCode.READ_REGISTERS,
        )

        return GrowattReadRegistersRequestMessage(
            header=header,
            datalogger_serial=self.session_state.datalogger_serial,
            register_start=command.register_start,
            register_end=command.register_end,
        )
