import pytest

from shine2mqtt.growatt.protocol.decoders.data import BufferDataRequestDecoder
from shine2mqtt.growatt.protocol.encoders.data import BufferedDataPayloadEncoder
from tests.utils.loader import CapturedFrameLoader

_, headers, payloads = CapturedFrameLoader.load("buffered_data_message")


@pytest.mark.parametrize(
    "header,payload", zip(headers, payloads, strict=True), ids=range(len(headers))
)
def test_encode_decode_buffered_data_message_roundtrip_preserves_data(header, payload) -> None:
    decoder = BufferDataRequestDecoder()
    encoder = BufferedDataPayloadEncoder()

    decoded_message = decoder.decode(header, payload)

    encoded_payload = encoder.encode(decoded_message)

    redecoded_message = decoder.decode(header, encoded_payload)

    assert decoded_message == redecoded_message
