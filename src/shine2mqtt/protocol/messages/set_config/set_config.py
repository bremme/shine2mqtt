from dataclasses import dataclass

from shine2mqtt.protocol.messages.message import DataloggerMessage


# Server messages ######################################################################
# responses
# request
@dataclass
class GrowattSetConfigRequestMessage(DataloggerMessage):
    register: int
    value: str


@dataclass
class GrowattSetConfigResponseMessage(DataloggerMessage):
    register: int
    ack: bool
