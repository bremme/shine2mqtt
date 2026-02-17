from dataclasses import dataclass

from shine2mqtt.growatt.protocol.ack.ack import GrowattAckMessage
from shine2mqtt.growatt.protocol.base.message import DataloggerMessage


# Server messages ######################################################################
# responses
# request
@dataclass
class GrowattSetConfigRequestMessage(DataloggerMessage):
    register: int
    value: str


@dataclass
class GrowattSetConfigResponseMessage(GrowattAckMessage):
    pass
