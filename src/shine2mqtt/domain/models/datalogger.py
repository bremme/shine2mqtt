from dataclasses import dataclass


@dataclass
class DataLogger:
    serial: str
    sw_version: str
    protocol_id: int
    unit_id: int
