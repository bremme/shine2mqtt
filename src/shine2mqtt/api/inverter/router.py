import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends

from shine2mqtt.api.constants import INVERTER_COMMAND_TIMEOUT_SECONDS
from shine2mqtt.api.dependencies import (
    get_command_executor,
)
from shine2mqtt.api.http_exceptions import (
    gateway_timeout_504,
    internal_server_error_500,
    not_implemented_501,
)
from shine2mqtt.api.inverter.mappers import read_registers_response_to_inverter_registers
from shine2mqtt.api.inverter.models import InverterRegister, RawFrameRequest
from shine2mqtt.app.command_executor import SessionCommandExecutor
from shine2mqtt.growatt.protocol.raw.raw import GrowattRawMessage
from shine2mqtt.growatt.server.protocol.session.command.command import (
    RawFrameCommand,
    ReadRegistersCommand,
)

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


# Inverter register endpoints
@router.get("/registers/{address}")
async def read_single_inverter_register(serial: str, address: int):
    not_implemented_501()


@router.get("/registers")
async def read_multiple_inverter_registers(
    serial: str,
    start: int,
    end: int,
    executer: Annotated[SessionCommandExecutor, Depends(get_command_executor)],
) -> list[InverterRegister]:
    command = ReadRegistersCommand(datalogger_serial=serial, register_start=start, register_end=end)

    try:
        async with asyncio.timeout(INVERTER_COMMAND_TIMEOUT_SECONDS):
            message = await executer.execute(command)
    except TimeoutError:
        gateway_timeout_504()
    # TODO invalid register exception
    except Exception as e:
        internal_server_error_500(e)

    return read_registers_response_to_inverter_registers(message)


@router.put("/registers/{address}")
async def write_single_inverter_register(serial: str, address: int, value: int):
    not_implemented_501()


@router.put("/registers")
async def write_multiple_inverter_registers(serial: str, registers: list[dict[str, int]]):
    not_implemented_501()


@router.post(
    "/raw-frames",
    responses={504: {"description": "Gateway timeout when the datalogger did not respond in time"}},
)
async def send_raw_frame(
    serial: str,
    request: RawFrameRequest,
    executer: Annotated[SessionCommandExecutor, Depends(get_command_executor)],
) -> GrowattRawMessage:
    command = RawFrameCommand(
        datalogger_serial=serial,
        function_code=request.function_code,
        protocol_id=request.protocol_id,
        payload=bytes.fromhex(request.payload),
    )

    try:
        async with asyncio.timeout(INVERTER_COMMAND_TIMEOUT_SECONDS):
            message = await executer.execute(command)
    except TimeoutError:
        gateway_timeout_504()

    return message
