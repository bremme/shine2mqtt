from asyncio import Future

from loguru import logger

from shine2mqtt.growatt.protocol.base.message import BaseMessage
from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.get_config.get_config import (
    GrowattGetConfigRequestMessage,
)
from shine2mqtt.growatt.protocol.header.header import MBAPHeader
from shine2mqtt.growatt.server.protocol.session.command.command import (
    BaseCommand,
    GetConfigByNameCommand,
    GetConfigByRegistersCommand,
)


class CommandHandler:
    def __init__(self, session_state, config_registry):
        self.session_state = session_state
        self.command_futures: dict[tuple[FunctionCode, int], Future] = {}
        self.config_registry = config_registry

    def handle_command(self, command: BaseCommand) -> BaseMessage | None:
        if isinstance(command, GetConfigByNameCommand):
            register = self.config_registry.get_register_by_name(command.name)
            if register is None:
                command.future.set_exception(ValueError(f"Unknown config name: {command.name}"))
                return
            message = self._build_get_config_request_message(
                register_start=register,
            )
            self.store_command_future(message.header, command.future)
            return message

        elif isinstance(command, GetConfigByRegistersCommand):
            if self.config_registry.get_register_info(command.register) is None:
                command.future.set_exception(
                    ValueError(f"Unknown config register: {command.register}")
                )
                return
            message = self._build_get_config_request_message(
                register_start=command.register,
            )
            self.store_command_future(message.header, command.future)
            return message

    def resolve_response(self, message: BaseMessage):
        if future := self.retrieve_command_future(message.header):
            future.set_result(message)
            logger.debug(
                f"Resolved command future for transaction ID {message.header.transaction_id}"
            )

    def store_command_future(self, header: MBAPHeader, future: Future) -> None:
        self.command_futures[(header.function_code, header.transaction_id)] = future

    def retrieve_command_future(self, header: MBAPHeader) -> Future | None:
        key = (header.function_code, header.transaction_id)
        return self.command_futures.pop(key, None)

    def _build_get_config_request_message(self, register_start, register_end=None):
        if register_end is None:
            register_end = register_start

        function_code = FunctionCode.GET_CONFIG
        transaction_id = self.session_state.get_transaction_id(function_code)

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
