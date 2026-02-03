from pathlib import Path

from shine2mqtt.growatt.protocol.frame.capturer.capturer import (
    CapturedFrame,
    FileFrameCapturer,
    FrameCapturer,
)
from shine2mqtt.growatt.protocol.frame.capturer.sanitizer import (
    RawPayloadSanitizer,
)
from shine2mqtt.growatt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.growatt.protocol.messages.header import MBAPHeader


class CaptureHandler:
    def __init__(
        self, encoder: FrameEncoder, capturer: FrameCapturer, sanitizer: RawPayloadSanitizer
    ):
        self.encoder = encoder
        self.capturer = capturer
        self.sanitizer = sanitizer

    @staticmethod
    def create(capture_dir: Path, encoder: FrameEncoder) -> "CaptureHandler":
        capturer = FileFrameCapturer(capture_dir)
        sanitizer = RawPayloadSanitizer.create()

        return CaptureHandler(encoder, capturer, sanitizer)

    def __call__(self, header: MBAPHeader, payload: bytes) -> None:
        sanitized_frame, sanitized_header, sanitized_payload = self.sanitizer.sanitize(
            header, payload
        )

        captured = CapturedFrame(
            frame=sanitized_frame,
            header=sanitized_header,
            payload=sanitized_payload,
        )
        self.capturer.capture(captured)
