from dataclasses import dataclass

from shine2mqtt.growatt.protocol.messages.base import DataloggerMessage


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
class GrowattSetConfigRequestMessage(DataloggerMessage):
    register: int
    length: int
    value: int | str


@dataclass
class GrowattGetConfigRequestMessage(DataloggerMessage):
    register_start: int
    register_end: int
