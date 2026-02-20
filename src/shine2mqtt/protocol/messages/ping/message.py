from dataclasses import dataclass

from shine2mqtt.protocol.messages.message import DataloggerMessage


@dataclass
class GrowattPingMessage(DataloggerMessage):
    pass
