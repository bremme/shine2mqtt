from dataclasses import dataclass

from shine2mqtt.growatt.protocol.base.message import DataloggerMessage


@dataclass
class GrowattPingMessage(DataloggerMessage):
    pass
