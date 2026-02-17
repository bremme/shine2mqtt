import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends

from shine2mqtt.api.constants import DATALOGGER_COMMAND_TIMEOUT_SECONDS
from shine2mqtt.api.datalogger.mappers import (
    get_config_response_to_datalogger_register_setting,
    get_config_response_to_datalogger_setting,
)
from shine2mqtt.api.datalogger.models import (
    Datalogger,
    DataloggerRegisterSetting,
    DataloggerSetting,
)
from shine2mqtt.api.dependencies import (
    get_command_executor,
    get_session_registry,
)
from shine2mqtt.api.http_exceptions import (
    bad_request_400,
    gateway_timeout_504,
    internal_server_error_500,
    not_found_404,
    not_implemented_501,
)
from shine2mqtt.app.command_executor import SessionCommandExecutor
from shine2mqtt.growatt.protocol.config import RegisterNotFoundError
from shine2mqtt.growatt.protocol.get_config.get_config import GrowattGetConfigResponseMessage
from shine2mqtt.growatt.protocol.set_config.set_config import GrowattSetConfigResponseMessage
from shine2mqtt.growatt.server.protocol.session.command.command import (
    GetConfigByNameCommand,
    GetConfigByRegisterCommand,
    SetConfigByNameCommand,
    SetConfigByRegisterCommand,
)
from shine2mqtt.growatt.server.protocol.session.registry import ProtocolSessionRegistry

router = APIRouter(tags=["datalogger"])


# Datalogger endpoints #############################################################################
@router.get(path="/dataloggers")
async def get_all_dataloggers(
    session_registry: Annotated[ProtocolSessionRegistry, Depends(get_session_registry)],
) -> list[Datalogger]:
    sessions = session_registry.get_all_sessions()

    return [
        Datalogger(
            serial=session.state.datalogger_serial,
            protocol_id=session.state.protocol_id,
            unit_id=session.state.unit_id,
        )
        for session in sessions
    ]


@router.get(path="/dataloggers/{serial}")
async def get_single_datalogger(
    serial: str,
    session_registry: Annotated[ProtocolSessionRegistry, Depends(get_session_registry)],
) -> Datalogger:
    session = session_registry.get_session(serial)

    if session is None:
        # added raise to make the type checker understand that session is not None after this point
        raise not_found_404(f"Datalogger with serial '{serial}' not found")

    return Datalogger(
        serial=session.state.datalogger_serial,
        protocol_id=session.state.protocol_id,
        unit_id=session.state.unit_id,
    )


# Datalogger settings endpoints ####################################################################
@router.get("/dataloggers/{serial}/settings")
async def get_all_datalogger_settings(
    serial: str,
    executer: Annotated[SessionCommandExecutor, Depends(get_command_executor)],
):
    # NOTE: this does not fit the current architecture were
    # one command maps to a Growatt message
    not_implemented_501()


@router.get("/dataloggers/{serial}/settings/{name}")
async def get_single_datalogger_setting(
    serial: str,
    name: str,
    executer: Annotated[SessionCommandExecutor, Depends(get_command_executor)],
) -> DataloggerSetting:
    command = GetConfigByNameCommand(datalogger_serial=serial, name=name)

    try:
        async with asyncio.timeout(DATALOGGER_COMMAND_TIMEOUT_SECONDS):
            message = await executer.execute(command)
    except TimeoutError:
        gateway_timeout_504()
    except RegisterNotFoundError:
        not_found_404(f"Setting with name '{name}' not found")
    except Exception as e:
        internal_server_error_500(e)

    return get_config_response_to_datalogger_setting(message)


@router.put("/dataloggers/{serial}/settings/{name}")
async def update_single_datalogger_setting(
    serial: str,
    name: str,
    value: str,
    executer: Annotated[SessionCommandExecutor, Depends(get_command_executor)],
) -> DataloggerSetting:
    command = SetConfigByNameCommand(datalogger_serial=serial, name=name, value=value)

    try:
        async with asyncio.timeout(DATALOGGER_COMMAND_TIMEOUT_SECONDS):
            message: GrowattSetConfigResponseMessage = await executer.execute(command)
    except TimeoutError:
        gateway_timeout_504()
    except RegisterNotFoundError:
        not_found_404(f"Setting with name '{name}' not found")
    except Exception as e:
        internal_server_error_500(e)

    if not message.ack:
        bad_request_400(f"Failed to update setting '{name}' with value '{value}'")

    return DataloggerSetting(name=name, value=value)


# Datalogger register endpoints ###############################################################################
@router.get("/dataloggers/{serial}/registers/{address}")
async def get_single_register(
    serial: str,
    address: int,
    executer: Annotated[SessionCommandExecutor, Depends(get_command_executor)],
) -> DataloggerRegisterSetting:
    command = GetConfigByRegisterCommand(datalogger_serial=serial, register=address)

    try:
        async with asyncio.timeout(DATALOGGER_COMMAND_TIMEOUT_SECONDS):
            message: GrowattGetConfigResponseMessage = await executer.execute(command)
    except TimeoutError:
        gateway_timeout_504()
    except KeyError:
        not_found_404(f"Register with address '{address}' not found")
    except Exception as e:
        internal_server_error_500(e)

    return get_config_response_to_datalogger_register_setting(message)


@router.get("/dataloggers/{serial}/registers")
async def get_all_registers(serial: str):
    # NOTE: this does not fit the current architecture were
    # one command maps to a Growatt message
    not_implemented_501()


@router.put("/dataloggers/{serial}/registers/{address}")
async def update_single_register(
    serial: str,
    address: int,
    value: str,
    executer: Annotated[SessionCommandExecutor, Depends(get_command_executor)],
) -> DataloggerRegisterSetting:
    command = SetConfigByRegisterCommand(datalogger_serial=serial, register=address, value=value)

    try:
        async with asyncio.timeout(DATALOGGER_COMMAND_TIMEOUT_SECONDS):
            message: GrowattSetConfigResponseMessage = await executer.execute(command)
    except TimeoutError:
        gateway_timeout_504()
    except RegisterNotFoundError:
        not_found_404(f"Register with address '{address}' not found")
    except Exception as e:
        internal_server_error_500(e)

    if not message.ack:
        bad_request_400(f"Failed to update register with address '{address}' and value '{value}'")

    return DataloggerRegisterSetting(
        address=address, value=value, raw_value=value.encode("ascii").hex()
    )
