from shine2mqtt.growatt.protocol.decoders.data import BufferDataRequestDecoder
from shine2mqtt.growatt.protocol.encoders.data import BufferedDataPayloadEncoder
from tests.utils.loader import CapturedFrameLoader

_, headers, payloads = CapturedFrameLoader.load("buffered_data_message")


class TestBufferedDataRoundtrip:
    @staticmethod
    def test_encode_decode_roundtrip_preserves_data() -> None:
        decoder = BufferDataRequestDecoder()
        encoder = BufferedDataPayloadEncoder()

        for header, payload in zip(headers, payloads, strict=True):
            decoded_message = decoder.decode(header, payload)

            encoded_payload = encoder.encode(decoded_message)

            redecoded_message = decoder.decode(header, encoded_payload)

            assert decoded_message == redecoded_message
