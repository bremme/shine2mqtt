from shine2mqtt.adapters.api.datalogger.models import DataloggerRegisterSetting, DataloggerSetting
from shine2mqtt.protocol.protocol.get_config.get_config import GrowattGetConfigResponseMessage


def get_config_response_to_datalogger_setting(
    message: GrowattGetConfigResponseMessage,
) -> DataloggerSetting:
    return DataloggerSetting(
        name=message.name if message.name else "unknown", value=str(message.value)
    )


def get_config_response_to_datalogger_register_setting(
    message: GrowattGetConfigResponseMessage,
) -> DataloggerRegisterSetting:
    return DataloggerRegisterSetting(
        address=message.register,
        value=message.value,
        raw_value=message.data.hex(),
    )
