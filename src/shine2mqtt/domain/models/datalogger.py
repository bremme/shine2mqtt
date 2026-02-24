from dataclasses import dataclass


@dataclass
class DataLogger:
    serial: str
    sw_version: str
    hw_version: str
    protocol_id: int
    unit_id: int
    ip_address: str
    mac_address: str
