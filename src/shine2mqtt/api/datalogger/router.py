from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

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
    gateway_timeout_504,
    get_command_executor,
    get_session_registry,
    internal_server_error_500,
    not_found_404,
    not_implemented_501,
)
from shine2mqtt.app.command_executor import SessionCommandExecutor
from shine2mqtt.growatt.protocol.config import RegisterNotFoundError
from shine2mqtt.growatt.server.protocol.session.command.command import (
    GetConfigByNameCommand,
    GetConfigByRegistersCommand,
    SetConfigByNameCommand,
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
    not_implemented_501()


@router.get("/dataloggers/{serial}/settings/{name}")
async def get_single_datalogger_setting(
    serial: str,
    name: str,
    executer: Annotated[SessionCommandExecutor, Depends(get_command_executor)],
) -> DataloggerSetting:
    command = GetConfigByNameCommand(datalogger_serial=serial, name=name)

    try:
        message = await executer.execute(command, timeout=10)
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
        message = await executer.execute(command, timeout=10)
    except TimeoutError:
        gateway_timeout_504()
    except RegisterNotFoundError:
        not_found_404(f"Setting with name '{name}' not found")
    except Exception as e:
        internal_server_error_500(e)

    if not message.ack:
        raise HTTPException(
            status_code=400, detail=f"Failed to update setting '{name}' with value '{value}'"
        )

    return DataloggerSetting(name=name, value=value)


# Register endpoints ###############################################################################
@router.get("/dataloggers/{serial}/registers/{register}")
async def get_single_register(
    serial: str,
    register: int,
    executer: Annotated[SessionCommandExecutor, Depends(get_command_executor)],
) -> DataloggerRegisterSetting:
    command = GetConfigByRegistersCommand(datalogger_serial=serial, register=register)

    try:
        message = await executer.execute(command, timeout=10)
    except TimeoutError:
        gateway_timeout_504()
    except KeyError:
        not_found_404(f"Register with number '{register}' not found")
    except Exception as e:
        internal_server_error_500(e)

    return get_config_response_to_datalogger_register_setting(message)


@router.get("/dataloggers/{serial}/registers")
async def get_all_registers(serial: str):
    not_implemented_501()


@router.put("/dataloggers/{serial}/registers/{register}")
async def update_single_register(serial: str, register: int, value: str):
    not_implemented_501()
