from pydantic import BaseModel, Field, field_validator, model_validator

from shine2mqtt.protocol.frame.header.header import FunctionCode


class InverterRegister(BaseModel):
    address: int
    value: int


class WriteMultipleRegistersRequest(BaseModel):
    register_start: int
    register_end: int
    values: str = Field(
        ..., description="Hex string payload (spaces allowed)", examples=["00 01 00 02", "0a0b0c0d"]
    )

    @property
    def values_as_bytes(self) -> bytes:
        return bytes.fromhex(self.values)

    @field_validator("values")
    @classmethod
    def validate_hex_values(cls, v: str) -> str:
        try:
            bytes.fromhex(v)
        except ValueError as e:
            raise ValueError("Invalid hex string") from e
        return v

    @model_validator(mode="after")
    def validate_values_length(self) -> WriteMultipleRegistersRequest:
        expected_bytes = (self.register_end - self.register_start + 1) * 2
        actual_bytes = len(bytes.fromhex(self.values))
        if actual_bytes != expected_bytes:
            raise ValueError(
                f"Expected {expected_bytes} bytes for register range "
                f"{self.register_start}–{self.register_end}, got {actual_bytes}"
            )
        return self


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
