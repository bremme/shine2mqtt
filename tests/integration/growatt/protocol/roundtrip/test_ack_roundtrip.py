import pytest

from shine2mqtt.growatt.protocol.ack.decoder import AckMessageResponseDecoder
from shine2mqtt.growatt.protocol.ack.encoder import AckPayloadEncoder
from tests.utils.loader import CapturedFrameLoader

_, headers, payloads = CapturedFrameLoader.load("set_config_response")


@pytest.mark.parametrize(
    "header,payload", zip(headers, payloads, strict=True), ids=range(len(headers))
)
def test_encode_decode_ack_message_roundtrip_preserves_data(header, payload) -> None:
    decoder = AckMessageResponseDecoder()
    encoder = AckPayloadEncoder()

    decoded_message = decoder.decode(header, payload)

    encoded_payload = encoder.encode(decoded_message)

    redecoded_message = decoder.decode(header, encoded_payload)

    assert decoded_message == redecoded_message
