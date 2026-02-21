from pydantic import BaseModel, Field, field_validator

from shine2mqtt.protocol.frame.header.header import FunctionCode


class InverterRegister(BaseModel):
    address: int
    value: int


class RawFrameResponse(BaseModel):
    payload: str


class RawFrameRequest(BaseModel):
    function_code: int = Field(..., description="Function code")
    payload: str = Field(
        ..., description="Hex string payload (spaces allowed)", examples=["00 01 00 02", "0a0b0c0d"]
    )

    @field_validator("function_code")
    @classmethod
    def validate_function_code(cls, v: int) -> int:
        try:
            FunctionCode(v)
        except ValueError as e:
            raise ValueError(f"Unknown function code: {v:#04x}") from e
        return v

    @field_validator("payload")
    @classmethod
    def validate_hex_payload(cls, v: str) -> str:
        try:
            bytes.fromhex(v)
        except ValueError as e:
            raise ValueError("Invalid hex string") from e
        return v
