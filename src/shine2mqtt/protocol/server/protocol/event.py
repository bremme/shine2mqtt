from dataclasses import dataclass

from shine2mqtt.protocol.protocol.base.message import BaseMessage


@dataclass
class ProtocolEvent:
    datalogger_serial: str
    message: BaseMessage
