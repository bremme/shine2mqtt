import pytest

from shine2mqtt.growatt.protocol.decoders.announce import AnnounceRequestDecoder
from shine2mqtt.growatt.protocol.decoders.config import GetConfigResponseDecoder
from shine2mqtt.growatt.protocol.decoders.data import DataRequestDecoder
from shine2mqtt.growatt.protocol.decoders.ping import PingRequestDecoder
from shine2mqtt.growatt.protocol.frame.capturer.sanitizer import (
    DUMMY_DATALOGGER_SERIAL,
    DUMMY_INVERTER_SERIAL,
    RawPayloadSanitizer,
)
from shine2mqtt.growatt.protocol.frame.crc import CRCCalculator
from shine2mqtt.growatt.protocol.frame.validator import FrameValidator
from tests.utils.loader import CapturedFrameLoader

announce_frames, announce_headers, announce_payloads = CapturedFrameLoader.load("announce_message")
data_frames, data_headers, data_payloads = CapturedFrameLoader.load("data_message")
get_config_frames, get_config_headers, get_config_payloads = CapturedFrameLoader.load(
    "get_config_message"
)
ping_frames, ping_headers, ping_payloads = CapturedFrameLoader.load("ping_message")

SENSITIVE_CONFIG_REGISTER_MAP = {
    14: "1.2.3.4",
    16: "00:11:22:33:44:55",
    17: "5.6.7.8",
    56: "MyWiFiNetwork",
    57: "MySecretPassword",
}


@pytest.fixture
def sanitizer():
    return RawPayloadSanitizer.create()


@pytest.fixture
def validator():
    return FrameValidator(CRCCalculator())


class TestSanitizerRoundtrip:
    @staticmethod
    @pytest.mark.parametrize(
        "frame, header, payload",
        zip(announce_frames, announce_headers, announce_payloads, strict=False),
    )
    def test_sanitizer_announce_payload(frame, header, payload, sanitizer, validator) -> None:
        decoder = AnnounceRequestDecoder()

        sanitized_frame, sanitized_header, sanitized_payload = sanitizer.sanitize(header, payload)

        validator.validate(sanitized_frame, sanitized_header)

        sanitized_message = decoder.decode(sanitized_header, sanitized_payload)

        assert len(sanitized_frame) == len(frame)
        assert len(sanitized_payload) == len(payload)
        assert sanitized_header == header
        assert sanitized_message.datalogger_serial == DUMMY_DATALOGGER_SERIAL
        assert sanitized_message.inverter_serial == DUMMY_INVERTER_SERIAL

    @staticmethod
    @pytest.mark.parametrize(
        "frame, header, payload",
        zip(data_frames, data_headers, data_payloads, strict=False),
    )
    def test_sanitizer_data_payload(frame, header, payload, sanitizer, validator) -> None:
        decoder = DataRequestDecoder()

        sanitized_frame, sanitized_header, sanitized_payload = sanitizer.sanitize(header, payload)

        validator.validate(sanitized_frame, sanitized_header)

        sanitized_message = decoder.decode(sanitized_header, sanitized_payload)

        assert len(sanitized_frame) == len(frame)
        assert len(sanitized_payload) == len(payload)
        assert sanitized_header == header
        assert sanitized_message.datalogger_serial == DUMMY_DATALOGGER_SERIAL
        assert sanitized_message.inverter_serial == DUMMY_INVERTER_SERIAL

    @staticmethod
    @pytest.mark.parametrize(
        "frame, header, payload",
        zip(get_config_frames, get_config_headers, get_config_payloads, strict=False),
    )
    def test_sanitize_get_config_payload(frame, header, payload, sanitizer, validator) -> None:
        decoder = GetConfigResponseDecoder()

        sanitized_frame, sanitized_header, sanitized_payload = sanitizer.sanitize(header, payload)
        validator.validate(sanitized_frame, sanitized_header)

        sanitized_message = decoder.decode(sanitized_header, sanitized_payload)

        if sanitized_message.register in SENSITIVE_CONFIG_REGISTER_MAP:
            assert (
                sanitized_message.value == SENSITIVE_CONFIG_REGISTER_MAP[sanitized_message.register]
            )

        assert sanitized_header == header
        assert sanitized_message.datalogger_serial == DUMMY_DATALOGGER_SERIAL

    @staticmethod
    @pytest.mark.parametrize(
        "frame, header, payload",
        zip(ping_frames, ping_headers, ping_payloads, strict=False),
    )
    def test_sanitizer_ping_payload(frame, header, payload, sanitizer, validator) -> None:
        decoder = PingRequestDecoder()

        for frame, header, payload in zip(ping_frames, ping_headers, ping_payloads, strict=True):
            sanitized_frame, sanitized_header, sanitized_payload = sanitizer.sanitize(
                header, payload
            )

            validator.validate(sanitized_frame, sanitized_header)

            sanitized_message = decoder.decode(sanitized_header, sanitized_payload)

            assert len(sanitized_frame) == len(frame)
            assert len(sanitized_payload) == len(payload)
            assert sanitized_header == header
            assert sanitized_message.datalogger_serial == DUMMY_DATALOGGER_SERIAL
