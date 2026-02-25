import pytest

from shine2mqtt.protocol.messages.announce.decoder import AnnounceRequestDecoder
from shine2mqtt.protocol.messages.announce.encoder import AnnouncePayloadEncoder
from tests.utils.loader import CapturedFrameLoader

_, headers, payloads = CapturedFrameLoader.load("announce_message")


@pytest.mark.parametrize(
    "header,payload", zip(headers, payloads, strict=True), ids=range(len(headers))
)
def test_encode_decode_announce_message_roundtrip_preserves_data(header, payload) -> None:
    decoder = AnnounceRequestDecoder()
    encoder = AnnouncePayloadEncoder()

    decoded_message = decoder.decode(header, payload)

    encoded_payload = encoder.encode(decoded_message)

    redecoded_message = decoder.decode(header, encoded_payload)

    assert decoded_message == redecoded_message
