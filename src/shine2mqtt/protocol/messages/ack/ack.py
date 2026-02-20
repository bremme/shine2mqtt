from dataclasses import dataclass

from shine2mqtt.protocol.messages.message import BaseMessage


@dataclass
class GrowattAckMessage(BaseMessage):
    ack: bool
