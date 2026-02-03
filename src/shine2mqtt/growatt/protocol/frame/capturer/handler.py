from shine2mqtt.growatt.protocol.frame.capturer.capturer import CapturedFrame, FrameCapturer
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

    # def __call__(self, message: BaseMessage) -> None:
    #     sanitized_message = self.sanitizer.sanitize(message)

    #     sanitized_frame = self.encoder.encode(sanitized_message)

    #     payload_encoder = self.encoder.encoder_registry.get_encoder(type(sanitized_message))

    #     sanitized_payload = payload_encoder.encode(sanitized_message)

    #     captured = CapturedFrame(
    #         frame=sanitized_frame,
    #         header=sanitized_message.header,
    #         payload=sanitized_payload,
    #     )
    #     self.capturer.capture(captured)
