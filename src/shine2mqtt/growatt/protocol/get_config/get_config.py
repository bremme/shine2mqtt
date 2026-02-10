from dataclasses import dataclass

from shine2mqtt.growatt.protocol.base.message import DataloggerMessage


# Client messages ######################################################################
# requests
# responses
@dataclass
class GrowattGetConfigResponseMessage(DataloggerMessage):
    register: int
    length: int
    data: bytes
    name: str | None = None
    description: str = ""
    value: int | str | None = None


# Server messages ######################################################################
# responses
# request
@dataclass
class GrowattGetConfigRequestMessage(DataloggerMessage):
    register_start: int
    register_end: int
