from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from shine2mqtt.api.datalogger.mappers import get_config_response_to_datalogger_setting
from shine2mqtt.api.datalogger.models import Datalogger, DataloggerSetting
from shine2mqtt.api.dependencies import get_command_executor, get_session_registry
from shine2mqtt.app.command_executor import SessionCommandExecutor
from shine2mqtt.growatt.protocol.get_config.get_config import GrowattGetConfigResponseMessage
from shine2mqtt.growatt.server.protocol.session.command.command import GetConfigByNameCommand
from shine2mqtt.growatt.server.protocol.session.registry import ProtocolSessionRegistry

router = APIRouter(tags=["datalogger"])


@router.get(path="/dataloggers")
async def get_all_datalogger(
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
        if session.state.datalogger_serial is not None and session.state.is_announced()
    ]


@router.get(path="/dataloggers/{serial}")
async def get_single_datalogger(
    serial: str,
    session_registry: Annotated[ProtocolSessionRegistry, Depends(get_session_registry)],
) -> Datalogger:
    session = session_registry.get_session(serial)

    if session is None or not session.state.is_announced():
        raise HTTPException(status_code=404, detail=f"Datalogger with serial {serial} not found")

    return Datalogger(
        serial=session.state.datalogger_serial,
        protocol_id=session.state.protocol_id,
        unit_id=session.state.unit_id,
    )


@router.get("/dataloggers/{serial}/settings")
async def get_all_datalogger_settings(serial: str) -> list[str]:
    return ["wifi_ssid", "mqtt_broker"]


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
        raise HTTPException(status_code=504, detail="Server timeout") from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    if message is None:
        raise HTTPException(status_code=404, detail=f"Config with name {name} not found") from None

    assert isinstance(message, GrowattGetConfigResponseMessage)
    return get_config_response_to_datalogger_setting(message)


@router.put("/dataloggers/{serial}/settings/{name}")
async def update_single_datalogger_setting(serial: str, name: str, value: str) -> dict[str, str]:
    return {"name": name, "value": value}


@router.get("/dataloggers/{serial}/registers/{register}")
async def get_single_register(serial: str, register: int) -> dict[str, str | int]:
    return {"register": register, "value": "example"}


@router.get("/dataloggers/{serial}/registers")
async def get_all_registers(serial: str) -> list[dict[str, str | int]]:
    return [{"register": 0, "value": "example"}]


@router.put("/dataloggers/{serial}/registers/{register}")
async def update_single_register(serial: str, register: int, value: str) -> dict[str, str | int]:
    return {"register": register, "value": value}
