import pytest

from shine2mqtt.protocol.messages.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.messages.ack.encoder import AckPayloadEncoder
from tests.utils.loader import CapturedFrameLoader

frames, headers, payloads = CapturedFrameLoader.load("ack_message")

# First payload is ACK (0x00), second is NACK (0x03)
INPUT_MESSAGES = [
    GrowattAckMessage(header=headers[0], ack=True),
    GrowattAckMessage(header=headers[1], ack=False),
]

EXPECTED_PAYLOADS = payloads

CASES = list(zip(INPUT_MESSAGES, EXPECTED_PAYLOADS, strict=True))


class TestAckPayloadEncoder:
    @pytest.fixture
    def encoder(self) -> AckPayloadEncoder:
        return AckPayloadEncoder()

    @pytest.mark.parametrize(
        "message,expected_payload", CASES, ids=[f"{i}" for i in range(len(CASES))]
    )
    def test_encode_ack_message_returns_valid_payload(self, encoder, message, expected_payload):
        payload = encoder.encode(message)

        assert payload == expected_payload

    def test_encode_ack_true_returns_ack_byte(self, encoder):
        message = GrowattAckMessage(
            header=headers[0],
            ack=True,
        )

        payload = encoder.encode(message)

        assert payload == b"\x00"

    def test_encode_ack_false_returns_nack_byte(self, encoder: AckPayloadEncoder):
        message = GrowattAckMessage(
            header=headers[0],
            ack=False,
        )

        payload = encoder.encode(message)

        assert payload == b"\x01"
