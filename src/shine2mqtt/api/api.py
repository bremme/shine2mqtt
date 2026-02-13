import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from loguru import logger
from pydantic import BaseModel, Field

from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.get_config.get_config import GrowattGetConfigResponseMessage
from shine2mqtt.growatt.protocol.header.header import MBAPHeader
from shine2mqtt.growatt.server.protocol.queues import ProtocolCommands
from shine2mqtt.growatt.server.protocol.session.command.command import (
    GetConfigByNameCommand,
    GetConfigByRegistersCommand,
    RawFrameCommand,
)


class HeaderRequest(BaseModel):
    transaction_id: int = Field(..., ge=0, le=65535, description="Transaction ID (0-65535)")
    protocol_id: int = Field(..., ge=0, le=65535, description="Protocol ID (0-65535)")
    length: int = Field(..., ge=0, le=65535, description="Length field (0-65535)")
    unit_id: int = Field(..., ge=0, le=255, description="Unit ID (0-255)")
    function_code: int = Field(..., ge=0, le=255, description="Function code (0-255)")


class RawFrameRequest(BaseModel):
    header: HeaderRequest
    payload: str = Field(
        ...,
        description="Hex string of the payload (without header). Spaces are allowed for readability, e.g. '00 01 00 02'",
    )


def create_app(protocol_commands: ProtocolCommands) -> FastAPI:
    app = FastAPI()

    def get_protocol_commands() -> ProtocolCommands:
        return protocol_commands

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")

    @app.get("/configs")
    async def get_config_by_name(
        commands: Annotated[ProtocolCommands, Depends(get_protocol_commands)],
        name: str = Query(..., description="Config name"),
    ) -> GrowattGetConfigResponseMessage:
        future = asyncio.get_running_loop().create_future()
        command = GetConfigByNameCommand(name=name, future=future)

        try:
            logger.debug(f"Enqueuing command: {command}")
            commands.put_nowait(command)
        except asyncio.QueueFull as e:
            raise HTTPException(status_code=503, detail="Server error") from e

        try:
            logger.debug(f"Waiting for command result: {command}")
            return await asyncio.wait_for(future, timeout=10)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except TimeoutError as e:
            raise HTTPException(status_code=504, detail="Server timeout") from e

    @app.get("/configs/{register}")
    async def get_config_by_register(
        register: int,
        commands: Annotated[ProtocolCommands, Depends(get_protocol_commands)],
    ) -> GrowattGetConfigResponseMessage:
        future = asyncio.get_running_loop().create_future()
        command = GetConfigByRegistersCommand(register=register, future=future)

        try:
            logger.debug(f"Enqueuing command: {command}")
            commands.put_nowait(command)
        except asyncio.QueueFull as e:
            raise HTTPException(status_code=503, detail="Server error") from e

        try:
            logger.debug(f"Waiting for command result: {command}")
            return await asyncio.wait_for(future, timeout=10)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except TimeoutError as e:
            raise HTTPException(status_code=504, detail="Server timeout") from e

    @app.post("/raw-frames")
    async def send_raw_frame(
        request: RawFrameRequest,
        command_queue: Annotated[ProtocolCommands, Depends(get_protocol_commands)],
    ):
        try:
            payload_bytes = bytes.fromhex(request.payload)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid payload hex string: {e}") from e

        try:
            function_code = FunctionCode(request.header.function_code)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid function code {request.header.function_code}: {e}",
            ) from e

        header = MBAPHeader(
            transaction_id=request.header.transaction_id,
            protocol_id=request.header.protocol_id,
            length=request.header.length,
            unit_id=request.header.unit_id,
            function_code=function_code,
        )

        future = asyncio.get_running_loop().create_future()
        command = RawFrameCommand(header=header, payload=payload_bytes, future=future)

        try:
            logger.debug(f"Enqueuing command: {command}")
            command_queue.put_nowait(command)
        except asyncio.QueueFull as e:
            raise HTTPException(status_code=503, detail="Server error") from e

        try:
            logger.debug(f"Waiting for command result: {command}")
            return await asyncio.wait_for(future, timeout=10)
        except TimeoutError as e:
            raise HTTPException(status_code=504, detail="Server timeout") from e

    return app
