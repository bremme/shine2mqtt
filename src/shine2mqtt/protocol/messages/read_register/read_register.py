from dataclasses import dataclass

from shine2mqtt.protocol.messages.message import DataloggerMessage


# Server messages ######################################################################
# request
@dataclass
class GrowattReadRegistersRequestMessage(DataloggerMessage):
    register_start: int
    register_end: int


# Datalogger messages ######################################################################
# response
@dataclass
class GrowattReadMultipleRegisterResponseMessage(DataloggerMessage):
    register_start: int
    register_end: int
    data: str
    data_u16: dict[int, int]
    # needs mapping
    names: list[str] | None = None
    descriptions: list[str] | None = None
    values: list[int | str] | None = None
