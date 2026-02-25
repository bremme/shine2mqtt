from dataclasses import dataclass


@dataclass
class DataLogger:
    serial: str
    protocol_id: int
    unit_id: int
    sw_version: str
    hw_version: str
    ip_address: str
    mac_address: str
