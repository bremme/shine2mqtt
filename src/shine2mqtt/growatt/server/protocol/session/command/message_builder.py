from asyncio import Future

from shine2mqtt.growatt.protocol.base.message import BaseMessage
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
    BaseCommand,
    GetConfigByNameCommand,
    GetConfigByRegisterCommand,
    RawFrameCommand,
    ReadRegistersCommand,
    SetConfigByRegisterCommand,
)
from shine2mqtt.growatt.server.protocol.session.state import ServerProtocolSessionState


class CommandMessageBuilder:
    def __init__(self, session_state: ServerProtocolSessionState, config_registry: ConfigRegistry):
        self.session_state = session_state
        self.command_futures: dict[tuple[FunctionCode, int], Future] = {}
        self.config_registry = config_registry

    def build_message(self, command: BaseCommand) -> BaseMessage:
        match command:
            case GetConfigByNameCommand():
                register = self.config_registry.get_register_by_name(command.name)

                message = self._build_get_config_request_message(
                    register_start=register,
                )

                return message
            case GetConfigByRegisterCommand():
                return self._build_get_config_request_message(
                    register_start=command.register,
                )

            case SetConfigByRegisterCommand():
                return self._build_set_config_request_message(
                    register=command.register, value=command.value
                )

            case RawFrameCommand():
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
            case ReadRegistersCommand():
                header = MBAPHeader(
                    transaction_id=self.session_state.get_next_transaction_id(
                        FunctionCode.READ_REGISTERS
                    ),
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
            case _:
                raise ValueError(f"Unknown command type: {type(command)}")

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

    def _build_set_config_request_message(self, register, value):
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
