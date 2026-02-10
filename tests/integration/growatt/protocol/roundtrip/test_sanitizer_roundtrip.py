import pytest

from shine2mqtt.growatt.protocol.announce.decoder import AnnounceRequestDecoder
from shine2mqtt.growatt.protocol.crc.decoder import CRCDecoder
from shine2mqtt.growatt.protocol.data.decoder import DataRequestDecoder
from shine2mqtt.growatt.protocol.frame.capturer.sanitizer import (
    DUMMY_DATALOGGER_SERIAL,
    DUMMY_INVERTER_SERIAL,
    RawPayloadSanitizer,
)
from shine2mqtt.growatt.protocol.frame.crc import CRCCalculator
from shine2mqtt.growatt.protocol.frame.validator import FrameValidator
from shine2mqtt.growatt.protocol.get_config.decoder import GetConfigResponseDecoder
from shine2mqtt.growatt.protocol.ping.decoder import PingRequestDecoder
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
    return FrameValidator(CRCCalculator(), CRCDecoder())


@pytest.mark.parametrize(
    "frame,header,payload",
    zip(announce_frames, announce_headers, announce_payloads, strict=True),
    ids=range(len(announce_frames)),
)
def test_sanitize_announce_message_preserves_structure(
    frame, header, payload, sanitizer, validator
) -> None:
    decoder = AnnounceRequestDecoder()

    sanitized_frame, sanitized_header, sanitized_payload = sanitizer.sanitize(header, payload)

    validator.validate(sanitized_frame, sanitized_header)

    sanitized_message = decoder.decode(sanitized_header, sanitized_payload)

    assert len(sanitized_frame) == len(frame)
    assert len(sanitized_payload) == len(payload)
    assert sanitized_header == header
    assert sanitized_message.datalogger_serial == DUMMY_DATALOGGER_SERIAL
    assert sanitized_message.inverter_serial == DUMMY_INVERTER_SERIAL


@pytest.mark.parametrize(
    "frame,header,payload",
    zip(data_frames, data_headers, data_payloads, strict=True),
    ids=range(len(data_frames)),
)
def test_sanitize_data_message_preserves_structure(
    frame, header, payload, sanitizer, validator
) -> None:
    decoder = DataRequestDecoder()

    sanitized_frame, sanitized_header, sanitized_payload = sanitizer.sanitize(header, payload)

    validator.validate(sanitized_frame, sanitized_header)

    sanitized_message = decoder.decode(sanitized_header, sanitized_payload)

    assert len(sanitized_frame) == len(frame)
    assert len(sanitized_payload) == len(payload)
    assert sanitized_header == header
    assert sanitized_message.datalogger_serial == DUMMY_DATALOGGER_SERIAL
    assert sanitized_message.inverter_serial == DUMMY_INVERTER_SERIAL


@pytest.mark.parametrize(
    "frame,header,payload",
    zip(get_config_frames, get_config_headers, get_config_payloads, strict=True),
    ids=range(len(get_config_frames)),
)
def test_sanitize_config_message_preserves_structure(
    frame, header, payload, sanitizer, validator
) -> None:
    decoder = GetConfigResponseDecoder()

    sanitized_frame, sanitized_header, sanitized_payload = sanitizer.sanitize(header, payload)
    validator.validate(sanitized_frame, sanitized_header)

    sanitized_message = decoder.decode(sanitized_header, sanitized_payload)

    if sanitized_message.register in SENSITIVE_CONFIG_REGISTER_MAP:
        assert sanitized_message.value == SENSITIVE_CONFIG_REGISTER_MAP[sanitized_message.register]

    assert sanitized_header == header
    assert sanitized_message.datalogger_serial == DUMMY_DATALOGGER_SERIAL


@pytest.mark.parametrize(
    "frame,header,payload",
    zip(ping_frames, ping_headers, ping_payloads, strict=True),
    ids=range(len(ping_frames)),
)
def test_sanitize_ping_message_preserves_structure(
    frame, header, payload, sanitizer, validator
) -> None:
    decoder = PingRequestDecoder()

    sanitized_frame, sanitized_header, sanitized_payload = sanitizer.sanitize(header, payload)

    validator.validate(sanitized_frame, sanitized_header)

    sanitized_message = decoder.decode(sanitized_header, sanitized_payload)

    assert len(sanitized_frame) == len(frame)
    assert len(sanitized_payload) == len(payload)
    assert sanitized_header == header
    assert sanitized_message.datalogger_serial == DUMMY_DATALOGGER_SERIAL
