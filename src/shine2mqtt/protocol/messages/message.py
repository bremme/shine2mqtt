from dataclasses import dataclass

from shine2mqtt.protocol.frame.header.header import MBAPHeader


@dataclass
class BaseMessage:
    header: MBAPHeader


@dataclass
class DataloggerMessage(BaseMessage):
    datalogger_serial: str
