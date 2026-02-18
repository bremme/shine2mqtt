from abc import ABC
from dataclasses import dataclass
from datetime import datetime

from shine2mqtt.domain.models.inverter import InverterSettings, InverterState


@dataclass(frozen=True)
class DomainEvent(ABC):
    datalogger_serial: str
    timestamp: datetime


@dataclass(frozen=True)
class InverterStateUpdatedEvent(DomainEvent):
    state: InverterState


@dataclass(frozen=True)
class DataloggerAnnouncedEvent(DomainEvent):
    inverter_serial: str
    inverter_settings: InverterSettings
