import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends

from shine2mqtt.adapters.api.constants import INVERTER_COMMAND_TIMEOUT_SECONDS
from shine2mqtt.adapters.api.dependencies import get_read_handler, get_send_raw_frame_handler
from shine2mqtt.adapters.api.http_exceptions import (
    gateway_timeout_504,
    internal_server_error_500,
    not_found_404,
    not_implemented_501,
)
from shine2mqtt.adapters.api.inverter.mappers import (
    inverter_registers_to_api_model,
    raw_bytes_to_api_model,
)
from shine2mqtt.adapters.api.inverter.models import (
    InverterRegister,
    RawFrameRequest,
    RawFrameResponse,
)
from shine2mqtt.app.exceptions import DataloggerNotConnectedError
from shine2mqtt.app.handlers.read_register import ReadRegisterHandler
from shine2mqtt.app.handlers.send_raw_frame import SendRawFrameHandler

router = APIRouter(prefix="/dataloggers/{serial}/inverter", tags=["inverter"])


@router.get("/settings")
async def get_all_inverter_settings(serial: str):
    not_implemented_501()


@router.get("/settings/{name}")
async def get_single_inverter_setting(serial: str, name: str):
    not_implemented_501()


@router.put("/settings/{name}")
async def update_single_inverter_setting(serial: str, name: str, value: str):
    not_implemented_501()


# Inverter (holding) register endpoints
@router.get("/registers/{address}")
async def read_single_inverter_register(
    serial: str,
    address: int,
    read_handler: Annotated[ReadRegisterHandler, Depends(get_read_handler)],
) -> InverterRegister:
    registers = await read_multiple_inverter_registers(serial, address, address, read_handler)
    if not registers:
        not_found_404(f"Register {address} not found")
    return registers[0]


@router.get("/registers")
async def read_multiple_inverter_registers(
    serial: str,
    start: int,
    end: int,
    read_handler: Annotated[ReadRegisterHandler, Depends(get_read_handler)],
) -> list[InverterRegister]:
    try:
        async with asyncio.timeout(INVERTER_COMMAND_TIMEOUT_SECONDS):
            data = await read_handler.read_inverter_registers(serial, start, end)
    except DataloggerNotConnectedError:
        not_found_404(f"Datalogger '{serial}' not connected")
    except TimeoutError:
        gateway_timeout_504()
    except Exception as e:
        internal_server_error_500(e)

    return inverter_registers_to_api_model(data)


@router.put("/registers/{address}")
async def write_single_inverter_register(serial: str, address: int, value: int):
    not_implemented_501()


@router.put("/registers")
async def write_multiple_inverter_registers(serial: str, registers: list[dict[str, int]]):
    not_implemented_501()


# Raw frame endpoints
@router.post(
    "/raw-frames",
    responses={504: {"description": "Gateway timeout when the datalogger did not respond in time"}},
)
async def send_raw_frame(
    serial: str,
    request: RawFrameRequest,
    handler: Annotated[SendRawFrameHandler, Depends(get_send_raw_frame_handler)],
) -> RawFrameResponse:
    try:
        async with asyncio.timeout(INVERTER_COMMAND_TIMEOUT_SECONDS):
            payload = await handler.send_raw_frame(
                serial,
                request.function_code,
                bytes.fromhex(request.payload),
            )
    except DataloggerNotConnectedError:
        not_found_404(f"Datalogger '{serial}' not connected")
    except TimeoutError:
        gateway_timeout_504()
    except Exception as e:
        internal_server_error_500(e)

    return raw_bytes_to_api_model(payload)
