import pytest

from shine2mqtt.growatt.protocol.encoders.ping import PingPayloadEncoder
from shine2mqtt.growatt.protocol.messages.ping import GrowattPingMessage
from tests.utils.loader import CapturedFrameLoader

frames, headers, payloads = CapturedFrameLoader.load("ping_message")

DATALOGGER_SERIAL = "XGDABCDEFG"

INPUT_MESSAGES = [
    GrowattPingMessage(
        header=header,
        datalogger_serial=DATALOGGER_SERIAL,
    )
    for header in headers
]

EXPECTED_PAYLOADS = payloads

CASES = list(zip(INPUT_MESSAGES, EXPECTED_PAYLOADS, strict=True))


class TestPingPayloadEncoder:
    @pytest.fixture
    def encoder(self):
        return PingPayloadEncoder()

    @pytest.mark.parametrize(
        "message,expected_payload", CASES, ids=[f"{i}" for i in range(len(CASES))]
    )
    def test_encode_ping_message_returns_valid_payload(self, encoder, message, expected_payload):
        payload = encoder.encode(message)

        assert payload == expected_payload
