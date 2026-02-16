from typing import Annotated

from fastapi import Depends, HTTPException, Request

from shine2mqtt.app.command_executor import SessionCommandExecutor
from shine2mqtt.growatt.server.protocol.session.registry import ProtocolSessionRegistry


def not_implemented_501():
    raise HTTPException(status_code=501, detail="Not implemented") from None


def gateway_timeout_504():
    raise HTTPException(status_code=504, detail="Server timeout") from None


def internal_server_error_500(e: Exception):
    raise HTTPException(status_code=500, detail=str(e)) from e


def bad_request_400(detail: str, e: Exception | None = None):
    raise HTTPException(status_code=400, detail=detail) from e


def not_found_404(detail: str):
    raise HTTPException(status_code=404, detail=detail) from None


def get_session_registry(request: Request) -> ProtocolSessionRegistry:
    return request.app.state.session_registry


def get_command_executor(
    serial: str, registry: Annotated[ProtocolSessionRegistry, Depends(get_session_registry)]
) -> SessionCommandExecutor:
    session = registry.get_session(serial)
    if not session:
        raise HTTPException(503, f"Datalogger with serial {serial} not connected")
    return SessionCommandExecutor(session)
