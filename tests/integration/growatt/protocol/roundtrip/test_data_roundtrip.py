from shine2mqtt.growatt.protocol.decoders.data import DataRequestDecoder
from shine2mqtt.growatt.protocol.encoders.data import DataPayloadEncoder
from tests.utils.loader import CapturedFrameLoader

_, headers, payloads = CapturedFrameLoader.load("data_message")


class TestDataRoundtrip:
    @staticmethod
    def test_encode_decode_roundtrip_preserves_data() -> None:
        decoder = DataRequestDecoder()
        encoder = DataPayloadEncoder()

        for header, payload in zip(headers, payloads, strict=True):
            decoded_message = decoder.decode(header, payload)

            encoded_payload = encoder.encode(decoded_message)

            redecoded_message = decoder.decode(header, encoded_payload)

            assert decoded_message == redecoded_message
