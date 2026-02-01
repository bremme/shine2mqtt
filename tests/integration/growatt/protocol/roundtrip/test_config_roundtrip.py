from shine2mqtt.growatt.protocol.decoders.config import GetConfigResponseDecoder
from shine2mqtt.growatt.protocol.encoders.config import GetConfigResponsePayloadEncoder
from tests.utils.loader import CapturedFrameLoader

_, headers, payloads = CapturedFrameLoader.load("get_config_message")


class TestConfigRoundtrip:
    @staticmethod
    def test_encode_decode_roundtrip_preserves_data() -> None:
        decoder = GetConfigResponseDecoder()
        encoder = GetConfigResponsePayloadEncoder()

        for header, payload in zip(headers, payloads, strict=True):
            decoded_message = decoder.decode(header, payload)

            encoded_payload = encoder.encode(decoded_message)

            redecoded_message = decoder.decode(header, encoded_payload)

            assert decoded_message == redecoded_message
