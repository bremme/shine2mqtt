from dataclasses import dataclass

from shine2mqtt.growatt.protocol.messages.header import MBAPHeader


@dataclass
class BaseMessage:
    header: MBAPHeader


@dataclass
class DataloggerMessage(BaseMessage):
    datalogger_serial: str
