from dataclasses import dataclass


# Use a bit shorter intervals compared to the real datalogger for better testing feedback loop
# default datalogger intervals: announce=30s, data=300s, ping=180s
@dataclass
class SimulatedClientConfig:
    enabled: bool = False
    server_host: str = "localhost"
    server_port: int = 5279
    announce_interval: int = 5
    data_interval: int = 20
    ping_interval: int = 10
