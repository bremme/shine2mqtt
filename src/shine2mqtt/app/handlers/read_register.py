from shine2mqtt.app.exceptions import DataloggerNotConnectedError
from shine2mqtt.domain.interfaces.registry import SessionRegistry
from shine2mqtt.domain.interfaces.session import Session
from shine2mqtt.domain.models.config import ConfigResult
from shine2mqtt.protocol.settings.registry import SettingsRegistry


class ReadRegisterHandler:
    def __init__(self, session_registry: SessionRegistry, settings_registry: SettingsRegistry):
        self._session_registry = session_registry
        self._settings_registry = settings_registry

    async def get_config_by_register(self, datalogger_serial: str, register: int) -> ConfigResult:
        session: Session | None = self._session_registry.get(datalogger_serial)
        if session is None:
            raise DataloggerNotConnectedError(datalogger_serial)
        return await session.get_config(register)

    async def get_config_by_name(self, datalogger_serial: str, name: str) -> ConfigResult:
        register = self._settings_registry.get_register_by_name(name)
        return await self.get_config_by_register(datalogger_serial, register)

    async def read_inverter_registers(
        self, datalogger_serial: str, register_start: int, register_end: int
    ) -> dict[int, int]:
        session = self._session_registry.get(datalogger_serial)
        if session is None:
            raise DataloggerNotConnectedError(datalogger_serial)
        return await session.read_registers(register_start, register_end)
