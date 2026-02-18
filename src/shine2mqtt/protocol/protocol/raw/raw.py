from dataclasses import dataclass

from shine2mqtt.protocol.protocol.base.message import DataloggerMessage


@dataclass
class GrowattRawMessage(DataloggerMessage):
    payload: bytes
