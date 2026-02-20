from dataclasses import dataclass
from datetime import datetime

from shine2mqtt.protocol.messages.message import DataloggerMessage


@dataclass
class SafetyFunction:
    spi: bool
    auto_test_start: bool
    low_voltage_fault_ride_through: bool
    frequency_derating: bool
    soft_start: bool
    demand_response_management_system: bool
    power_voltage_control: bool
    high_voltage_fault_ride_through: bool
    rate_of_change_of_frequency_protection: bool
    frequency_derating_recovery: bool


# Datalogger messages ######################################################################
# requests
@dataclass
class GrowattAnnounceMessage(DataloggerMessage):
    inverter_serial: str

    remote_on_off: bool
    safety_function: SafetyFunction
    power_factor_memory: bool
    active_power_ac_max: int
    reactive_power_ac_max: int
    power_factor: float
    rated_power_ac: float
    rated_voltage_dc: float
    inverter_fw_version: str
    inverter_control_fw_version: str
    lcd_language: str
    device_type: str
    timestamp: datetime

    voltage_ac_low_limit: float
    voltage_ac_high_limit: float
    frequency_ac_low_limit: float
    frequency_ac_high_limit: float
    power_factor_control_mode: str
