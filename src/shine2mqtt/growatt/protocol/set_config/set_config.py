from dataclasses import dataclass

from shine2mqtt.growatt.protocol.base.message import DataloggerMessage


# Server messages ######################################################################
# responses
# request
@dataclass
class GrowattSetConfigRequestMessage(DataloggerMessage):
    register: int
    length: int
    value: int | str
