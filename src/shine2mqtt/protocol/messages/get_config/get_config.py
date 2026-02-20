from dataclasses import dataclass

from shine2mqtt.protocol.messages.message import DataloggerMessage

# Datalogger messages ######################################################################


# responses
@dataclass
class GrowattGetConfigResponseMessage(DataloggerMessage):
    register: int
    data: bytes
    value: str
    name: str | None = None
    description: str = ""


# Server messages ######################################################################


# request
@dataclass
class GrowattGetConfigRequestMessage(DataloggerMessage):
    register_start: int
    register_end: int
