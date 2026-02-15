from dataclasses import dataclass

from shine2mqtt.growatt.protocol.header.header import MBAPHeader


@dataclass
class BaseCommand:
    datalogger_serial: str


@dataclass
class GetConfigByNameCommand(BaseCommand):
    name: str


@dataclass
class GetConfigByRegistersCommand(BaseCommand):
    register: int


@dataclass
class ReadRegistersCommand(BaseCommand):
    register_start: int
    register_end: int


@dataclass
class RawFrameCommand(BaseCommand):
    header: MBAPHeader
    payload: bytes
