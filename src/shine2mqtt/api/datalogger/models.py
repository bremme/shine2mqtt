from pydantic import BaseModel, Field


class DataloggerSetting(BaseModel):
    name: str
    value: str


class DataloggerRegisterSetting(BaseModel):
    address: int
    value: str


class Datalogger(BaseModel):
    serial: str = Field(..., description="The serial number of the datalogger")
    protocol_id: int = Field(..., description="The protocol ID of the datalogger")
    unit_id: int = Field(..., description="The unit ID of the datalogger")
