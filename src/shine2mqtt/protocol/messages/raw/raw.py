from dataclasses import dataclass

from shine2mqtt.protocol.messages.message import DataloggerMessage


@dataclass
class GrowattRawRequestMessage(DataloggerMessage):
    payload: bytes
