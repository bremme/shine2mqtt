from typing import Annotated

from fastapi import Depends, HTTPException, Request

from shine2mqtt.app.command_executor import SessionCommandExecutor
from shine2mqtt.growatt.server.protocol.session.registry import ProtocolSessionRegistry


def get_session_registry(request: Request) -> ProtocolSessionRegistry:
    return request.app.state.session_registry


def get_command_executor(
    serial: str, registry: Annotated[ProtocolSessionRegistry, Depends(get_session_registry)]
) -> SessionCommandExecutor:
    session = registry.get_session(serial)
    if not session:
        raise HTTPException(503, f"Datalogger with serial {serial} not connected")
    return SessionCommandExecutor(session)
