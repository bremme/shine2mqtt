import pytest

from shine2mqtt.protocol.protocol.ping.decoder import PingRequestDecoder
from shine2mqtt.protocol.protocol.ping.encoder import PingPayloadEncoder
from tests.utils.loader import CapturedFrameLoader

_, headers, payloads = CapturedFrameLoader.load("ping_message")


@pytest.mark.parametrize(
    "header,payload", zip(headers, payloads, strict=True), ids=range(len(headers))
)
def test_encode_decode_ping_message_roundtrip_preserves_data(header, payload) -> None:
    decoder = PingRequestDecoder()
    encoder = PingPayloadEncoder()

    decoded_message = decoder.decode(header, payload)

    encoded_payload = encoder.encode(decoded_message)

    redecoded_message = decoder.decode(header, encoded_payload)

    assert decoded_message == redecoded_message
