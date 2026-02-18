from dataclasses import dataclass


@dataclass
class GetDataloggerSettingByNameCommand:
    name: str


@dataclass
class UpdateDataloggerSettingByNameCommand:
    name: str
    value: str


@dataclass
class GetDataloggerSettingByRegisterCommand:
    register: int


@dataclass
class UpdateDataloggerSettingByRegisterCommand:
    register: int
    value: str


@dataclass
class ReadInverterRegistersCommand:
    register_start: int
    register_end: int


@dataclass
class SendInverterRawFrameCommand:
    function_code: int
    protocol_id: int
    payload: bytes
