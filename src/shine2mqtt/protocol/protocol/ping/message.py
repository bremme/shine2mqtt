from dataclasses import dataclass

from shine2mqtt.protocol.protocol.base.message import DataloggerMessage


@dataclass
class GrowattPingMessage(DataloggerMessage):
    pass
