from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigResult:
    register: int
    value: str
    raw_data: bytes
    name: str | None = None
