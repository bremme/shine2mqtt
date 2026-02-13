import asyncio
from dataclasses import dataclass

from shine2mqtt.growatt.protocol.header.header import MBAPHeader


@dataclass
class BaseCommand:
    future: asyncio.Future


@dataclass
class GetConfigByNameCommand(BaseCommand):
    name: str


@dataclass
class GetConfigByRegistersCommand(BaseCommand):
    register: int


@dataclass
class ReadMultipleHoldingRegistersCommand(BaseCommand):
    register_start: int
    num_registers: int


@dataclass
class RawFrameCommand(BaseCommand):
    header: MBAPHeader
    payload: bytes
