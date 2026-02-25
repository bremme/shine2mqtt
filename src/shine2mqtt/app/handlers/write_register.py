from shine2mqtt.app.exceptions import DataloggerNotConnectedError
from shine2mqtt.domain.interfaces.registry import SessionRegistry
from shine2mqtt.domain.interfaces.session import Session
from shine2mqtt.protocol.settings.registry import SettingsRegistry


class WriteRegisterHandler:
    def __init__(self, session_registry: SessionRegistry, settings_registry: SettingsRegistry):
        self._session_registry = session_registry
        self._settings_registry = settings_registry

    async def set_config_by_register(
        self, datalogger_serial: str, register: int, value: str
    ) -> bool:
        session = self._session_registry.get(datalogger_serial)
        if session is None:
            raise DataloggerNotConnectedError(datalogger_serial)
        return await session.set_config(register, value)

    async def set_config_by_name(self, datalogger_serial: str, name: str, value: str) -> bool:
        register = self._settings_registry.get_register_by_name(name)
        return await self.set_config_by_register(datalogger_serial, register, value)

    async def write_single_inverter_register(
        self, datalogger_serial: str, register: int, value: int
    ) -> bool:
        session: Session | None = self._session_registry.get(datalogger_serial)
        if session is None:
            raise DataloggerNotConnectedError(datalogger_serial)
        return await session.write_single_register(register, value)

    async def write_multiple_inverter_registers(
        self, datalogger_serial: str, register_start: int, register_end: int, values: bytes
    ) -> bool:
        session: Session | None = self._session_registry.get(datalogger_serial)
        if session is None:
            raise DataloggerNotConnectedError(datalogger_serial)
        return await session.write_multiple_registers(register_start, register_end, values)
