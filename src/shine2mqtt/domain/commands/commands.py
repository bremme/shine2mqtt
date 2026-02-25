from dataclasses import dataclass


@dataclass
class GetDataloggerSettingByNameCommand:
    datalogger_serial: str
    name: str


@dataclass
class UpdateDataloggerSettingByNameCommand:
    datalogger_serial: str
    name: str
    value: str


@dataclass
class GetDataloggerSettingByRegisterCommand:
    datalogger_serial: str
    register: int


@dataclass
class UpdateDataloggerSettingByRegisterCommand:
    datalogger_serial: str
    register: int
    value: str


@dataclass
class ReadInverterRegistersCommand:
    datalogger_serial: str
    register_start: int
    register_end: int


@dataclass
class SendInverterRawFrameCommand:
    datalogger_serial: str
    function_code: int
    protocol_id: int
    payload: bytes
