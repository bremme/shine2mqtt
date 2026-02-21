import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends

from shine2mqtt.adapters.api.constants import DATALOGGER_COMMAND_TIMEOUT_SECONDS
from shine2mqtt.adapters.api.datalogger.mappers import (
    config_result_to_datalogger_register_setting,
    config_result_to_datalogger_setting,
)
from shine2mqtt.adapters.api.datalogger.models import (
    Datalogger,
    DataloggerRegisterSetting,
    DataloggerSetting,
)
from shine2mqtt.adapters.api.dependencies import (
    get_read_handler,
    get_session_registry,
    get_write_handler,
)
from shine2mqtt.adapters.api.http_exceptions import (
    bad_request_400,
    gateway_timeout_504,
    internal_server_error_500,
    not_found_404,
    not_implemented_501,
)
from shine2mqtt.app.exceptions import DataloggerNotConnectedError
from shine2mqtt.app.handlers.read_register import ReadRegisterHandler
from shine2mqtt.app.handlers.write_register import WriteRegisterHandler
from shine2mqtt.protocol.session.registry import ProtocolSessionRegistry
from shine2mqtt.protocol.settings.registry import RegisterNotFoundError

router = APIRouter(tags=["datalogger"])


@router.get(path="/dataloggers")
async def get_all_dataloggers(
    session_registry: Annotated[ProtocolSessionRegistry, Depends(get_session_registry)],
) -> list[Datalogger]:
    return [
        Datalogger(
            serial=session.datalogger.serial,
            protocol_id=session.datalogger.protocol_id,
            unit_id=session.datalogger.unit_id,
        )
        for session in session_registry.get_all()
    ]


@router.get(path="/dataloggers/{serial}")
async def get_single_datalogger(
    serial: str,
    session_registry: Annotated[ProtocolSessionRegistry, Depends(get_session_registry)],
) -> Datalogger:
    session = session_registry.get(serial)
    if session is None:
        not_found_404(f"Datalogger with serial '{serial}' not found")
    assert session is not None
    return Datalogger(
        serial=session.datalogger.serial,
        protocol_id=session.datalogger.protocol_id,
        unit_id=session.datalogger.unit_id,
    )


# Settings endpoints ###############################################################################


@router.get("/dataloggers/{serial}/settings")
async def get_all_datalogger_settings(serial: str):
    not_implemented_501()


@router.get("/dataloggers/{serial}/settings/{name}")
async def get_single_datalogger_setting(
    serial: str,
    name: str,
    read_handler: Annotated[ReadRegisterHandler, Depends(get_read_handler)],
) -> DataloggerSetting:
    try:
        async with asyncio.timeout(DATALOGGER_COMMAND_TIMEOUT_SECONDS):
            result = await read_handler.get_config_by_name(serial, name)
    except DataloggerNotConnectedError:
        not_found_404(f"Datalogger '{serial}' not connected")
    except RegisterNotFoundError:
        not_found_404(f"Setting '{name}' not found")
    except TimeoutError:
        gateway_timeout_504()
    except Exception as e:
        internal_server_error_500(e)
    return config_result_to_datalogger_setting(result)


@router.put("/dataloggers/{serial}/settings/{name}")
async def update_single_datalogger_setting(
    serial: str,
    name: str,
    value: str,
    write_handler: Annotated[WriteRegisterHandler, Depends(get_write_handler)],
) -> DataloggerSetting:
    try:
        async with asyncio.timeout(DATALOGGER_COMMAND_TIMEOUT_SECONDS):
            ack = await write_handler.set_config_by_name(serial, name, value)
    except DataloggerNotConnectedError:
        not_found_404(f"Datalogger '{serial}' not connected")
    except RegisterNotFoundError:
        not_found_404(f"Setting '{name}' not found")
    except TimeoutError:
        gateway_timeout_504()
    except Exception as e:
        internal_server_error_500(e)
    if not ack:
        bad_request_400(f"Failed to update setting '{name}' with value '{value}'")
    return DataloggerSetting(name=name, value=value)


# Register endpoints ###############################################################################


@router.get("/dataloggers/{serial}/registers")
async def get_all_registers(serial: str):
    not_implemented_501()


@router.get("/dataloggers/{serial}/registers/{address}")
async def get_single_register(
    serial: str,
    address: int,
    read_handler: Annotated[ReadRegisterHandler, Depends(get_read_handler)],
) -> DataloggerRegisterSetting:
    try:
        async with asyncio.timeout(DATALOGGER_COMMAND_TIMEOUT_SECONDS):
            result = await read_handler.get_config_by_register(serial, address)
    except DataloggerNotConnectedError:
        not_found_404(f"Datalogger '{serial}' not connected")
    except TimeoutError:
        gateway_timeout_504()
    except Exception as e:
        internal_server_error_500(e)
    return config_result_to_datalogger_register_setting(result)


@router.put("/dataloggers/{serial}/registers/{address}")
async def update_single_register(
    serial: str,
    address: int,
    value: str,
    write_handler: Annotated[WriteRegisterHandler, Depends(get_write_handler)],
) -> DataloggerRegisterSetting:
    try:
        async with asyncio.timeout(DATALOGGER_COMMAND_TIMEOUT_SECONDS):
            ack = await write_handler.set_config_by_register(serial, address, value)
    except DataloggerNotConnectedError:
        not_found_404(f"Datalogger '{serial}' not connected")
    except TimeoutError:
        gateway_timeout_504()
    except Exception as e:
        internal_server_error_500(e)
    if not ack:
        bad_request_400(f"Failed to update register {address} with value '{value}'")
    return DataloggerRegisterSetting(
        address=address, value=value, raw_value=value.encode("ascii").hex()
    )
