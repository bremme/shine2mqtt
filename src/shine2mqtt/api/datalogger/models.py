from pydantic import BaseModel


class DataloggerSetting(BaseModel):
    name: str
    value: str


class Datalogger(BaseModel):
    serial: str
    protocol_id: int
    unit_id: int
