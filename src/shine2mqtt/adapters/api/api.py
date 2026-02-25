from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse

from shine2mqtt.adapters.api.datalogger.router import router as datalogger_router
from shine2mqtt.adapters.api.inverter.router import router as inverter_router
from shine2mqtt.app.handlers.read_register import ReadRegisterHandler
from shine2mqtt.app.handlers.send_raw_frame import SendRawFrameHandler
from shine2mqtt.app.handlers.write_register import WriteRegisterHandler
from shine2mqtt.domain.interfaces.registry import SessionRegistry


def create_app(
    session_registry: SessionRegistry,
    read_handler: ReadRegisterHandler,
    write_handler: WriteRegisterHandler,
    send_raw_frame_handler: SendRawFrameHandler,
) -> FastAPI:
    app = FastAPI()

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")

    app.include_router(datalogger_router)
    app.include_router(inverter_router)

    @app.post("/coffee", status_code=418, tags=["coffee"])
    async def brew_coffee() -> Response:
        """Attempt to brew coffee with a teapot (RFC 2324)."""
        return Response(
            content="I'm a teapot. The resulting entity body MAY be short and stout.",
            status_code=418,
            media_type="text/plain",
        )

    app.state.session_registry = session_registry
    app.state.read_handler = read_handler
    app.state.write_handler = write_handler
    app.state.send_raw_frame_handler = send_raw_frame_handler

    return app
