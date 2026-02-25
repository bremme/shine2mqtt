from shine2mqtt.app.exceptions import DataloggerNotConnectedError
from shine2mqtt.domain.interfaces.registry import SessionRegistry


class SendRawFrameHandler:
    def __init__(self, session_registry: SessionRegistry):
        self._session_registry = session_registry

    async def send_raw_frame(
        self, datalogger_serial: str, function_code: int, payload: bytes
    ) -> bytes:
        session = self._session_registry.get(datalogger_serial)
        if session is None:
            raise DataloggerNotConnectedError(datalogger_serial)
        return await session.send_raw_frame(function_code, payload)
