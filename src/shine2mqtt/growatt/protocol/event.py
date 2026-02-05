from dataclasses import dataclass

from shine2mqtt.growatt.protocol.messages.base import BaseMessage


@dataclass
class ProtocolEvent:
    datalogger_serial: str
    message: BaseMessage
