from abc import ABC
from asyncio import Queue
from dataclasses import dataclass
from datetime import datetime

from shine2mqtt.domain.models.datalogger import DataLogger
from shine2mqtt.domain.models.inverter import Inverter, InverterState

DomainEvents = Queue["DomainEvent"]


@dataclass(frozen=True)
class DomainEvent(ABC):
    datalogger_serial: str
    timestamp: datetime


@dataclass(frozen=True)
class DataloggerAnnouncedEvent(DomainEvent):
    datalogger: DataLogger
    inverter: Inverter


@dataclass(frozen=True)
class InverterStateUpdatedEvent(DomainEvent):
    state: InverterState
