from dataclasses import dataclass

from shine2mqtt.growatt.protocol.base.message import BaseMessage


@dataclass
class GrowattAckMessage(BaseMessage):
    ack: bool
