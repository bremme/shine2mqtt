from dataclasses import dataclass

from shine2mqtt.growatt.protocol.messages.base import DataloggerMessage


@dataclass
class GrowattPingMessage(DataloggerMessage):
    pass
