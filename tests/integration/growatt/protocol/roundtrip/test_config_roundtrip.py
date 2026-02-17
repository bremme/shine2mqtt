import pytest

from shine2mqtt.growatt.protocol.get_config.decoder import GetConfigResponseDecoder
from shine2mqtt.growatt.protocol.get_config.encoder import GetConfigResponsePayloadEncoder
from tests.utils.loader import CapturedFrameLoader

_, headers, payloads = CapturedFrameLoader.load("get_config_response")


@pytest.mark.parametrize(
    "header,payload", zip(headers, payloads, strict=True), ids=range(len(headers))
)
def test_encode_decode_config_message_roundtrip_preserves_data(header, payload) -> None:
    decoder = GetConfigResponseDecoder()
    encoder = GetConfigResponsePayloadEncoder()

    decoded_message = decoder.decode(header, payload)

    encoded_payload = encoder.encode(decoded_message)

    redecoded_message = decoder.decode(header, encoded_payload)

    assert decoded_message == redecoded_message
