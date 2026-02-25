from shine2mqtt.adapters.api.datalogger.models import DataloggerRegisterSetting, DataloggerSetting
from shine2mqtt.domain.models.config import ConfigResult


def config_result_to_datalogger_setting(result: ConfigResult) -> DataloggerSetting:
    return DataloggerSetting(
        name=result.name if result.name else "unknown",
        value=result.value,
    )


def config_result_to_datalogger_register_setting(result: ConfigResult) -> DataloggerRegisterSetting:
    return DataloggerRegisterSetting(
        address=result.register,
        value=result.value,
        raw_value=result.raw_data.hex(),
    )
