from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Inverter:
    serial: str
    fw_version: str
    control_fw_version: str
    # device_type: str
    settings: InverterSettings


class InverterStatus(Enum):
    WAITING = 0
    NORMAL = 1
    FAULT = 3


@dataclass(frozen=True)
class InverterSettings:
    remote_on_off: bool
    safety_function: SafetyFunction
    power_factor_memory: bool
    active_power_ac_max: int
    reactive_power_ac_max: int
    power_factor: float
    rated_power_ac: float
    rated_voltage_dc: float
    # inverter_fw_version: str
    # inverter_control_fw_version: str
    # lcd_language: str
    # timestamp: datetime

    voltage_ac_low_limit: float
    voltage_ac_high_limit: float
    frequency_ac_low_limit: float
    frequency_ac_high_limit: float
    power_factor_control_mode: str


@dataclass(frozen=True)
class InverterState:
    inverter_status: InverterStatus
    # DC
    power_dc: float
    # DC 1
    voltage_dc_1: float
    current_dc_1: float
    power_dc_1: float
    # DC 2
    voltage_dc_2: float
    current_dc_2: float
    power_dc_2: float
    # AC
    power_ac: float
    frequency_ac: float
    # AC 1
    voltage_ac_1: float
    current_ac_1: float
    power_ac_1: float
    # AC line
    voltage_ac_l1_l2: float
    voltage_ac_l2_l3: float
    voltage_ac_l3_l1: float
    #
    total_run_time: int
    # Energy AC
    energy_ac_today: float
    energy_ac_total: float
    # Energy DC 1
    energy_dc_1_today: float
    energy_dc_1_total: float
    # Energy DC 2
    energy_dc_2_today: float
    energy_dc_2_total: float
    # Energy DC
    energy_dc_total: float
    # Temperatures
    temperature: float


@dataclass(frozen=True)
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
