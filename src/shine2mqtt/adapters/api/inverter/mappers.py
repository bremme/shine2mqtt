from shine2mqtt.adapters.api.inverter.models import InverterRegister, RawFrameResponse


def inverter_registers_to_api_model(data: dict[int, int]) -> list[InverterRegister]:
    return [InverterRegister(address=register, value=value) for register, value in data.items()]


def raw_bytes_to_raw_frame_response(payload: bytes) -> RawFrameResponse:
    return RawFrameResponse(payload=payload.hex())
