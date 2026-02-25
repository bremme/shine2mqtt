from fastapi import Request

from shine2mqtt.app.handlers.read_register import ReadRegisterHandler
from shine2mqtt.app.handlers.send_raw_frame import SendRawFrameHandler
from shine2mqtt.app.handlers.write_register import WriteRegisterHandler
from shine2mqtt.protocol.session.registry import ProtocolSessionRegistry


def get_session_registry(request: Request) -> ProtocolSessionRegistry:
    return request.app.state.session_registry


def get_read_handler(request: Request) -> ReadRegisterHandler:
    return request.app.state.read_handler


def get_write_handler(request: Request) -> WriteRegisterHandler:
    return request.app.state.write_handler


def get_send_raw_frame_handler(request: Request) -> SendRawFrameHandler:
    return request.app.state.send_raw_frame_handler
