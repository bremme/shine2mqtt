from shine2mqtt.growatt.protocol.decoders.ping import PingRequestDecoder
from shine2mqtt.growatt.protocol.encoders.ping import PingPayloadEncoder
from tests.utils.loader import CapturedFrameLoader

_, headers, payloads = CapturedFrameLoader.load("ping_message")


class TestPingRoundtrip:
    @staticmethod
    def test_encode_decode_roundtrip_preserves_data() -> None:
        decoder = PingRequestDecoder()
        encoder = PingPayloadEncoder()

        for header, payload in zip(headers, payloads, strict=True):
            decoded_message = decoder.decode(header, payload)

            encoded_payload = encoder.encode(decoded_message)

            redecoded_message = decoder.decode(header, encoded_payload)

            assert decoded_message == redecoded_message
