import time
from typing import Protocol


class ClockService(Protocol):
    def now(self) -> float:
        pass


class MonotonicClockService:
    def now(self) -> float:
        return time.monotonic()


def has_interval_elapsed(now: float, last_time: float, interval: int) -> bool:
    elapsed = now - last_time
    return elapsed >= interval
