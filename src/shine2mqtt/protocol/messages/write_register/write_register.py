from dataclasses import dataclass

from shine2mqtt.protocol.messages.message import DataloggerMessage


# Server messages ######################################################################
# responses
# request
@dataclass
class GrowattWriteSingleRegisterRequestMessage(DataloggerMessage):
    register: int
    value: int


@dataclass
class GrowattWriteMultipleRegistersRequestMessage(DataloggerMessage):
    register_start: int
    register_end: int
    values: bytes


# Datalogger messages ##################################################################
# responses
@dataclass
class GrowattWriteSingleRegisterResponseMessage(DataloggerMessage):
    register: int
    ack: bool
    value: int


@dataclass
class GrowattWriteMultipleRegistersResponseMessage(DataloggerMessage):
    register_start: int
    register_end: int
    ack: bool
