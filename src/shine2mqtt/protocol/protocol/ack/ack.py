from dataclasses import dataclass

from shine2mqtt.protocol.protocol.base.message import BaseMessage


@dataclass
class GrowattAckMessage(BaseMessage):
    ack: bool
