from dataclasses import dataclass

from shine2mqtt.growatt.protocol.base.message import DataloggerMessage

# Datalogger messages ######################################################################


# responses
@dataclass
class GrowattGetConfigResponseMessage(DataloggerMessage):
    register: int
    data: bytes
    name: str | None = None
    description: str = ""
    value: str | None = None


# Server messages ######################################################################


# request
@dataclass
class GrowattGetConfigRequestMessage(DataloggerMessage):
    register_start: int
    register_end: int
