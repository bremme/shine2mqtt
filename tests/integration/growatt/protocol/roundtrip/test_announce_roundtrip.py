from shine2mqtt.growatt.protocol.decoders.announce import AnnounceRequestDecoder
from shine2mqtt.growatt.protocol.encoders.announce import AnnouncePayloadEncoder
from tests.utils.loader import CapturedFrameLoader

_, headers, payloads = CapturedFrameLoader.load("announce_message")


class TestAnnounceRoundtrip:
    @staticmethod
    def test_encode_decode_roundtrip_preserves_data() -> None:
        decoder = AnnounceRequestDecoder()
        encoder = AnnouncePayloadEncoder()

        for header, payload in zip(headers, payloads, strict=True):
            decoded_message = decoder.decode(header, payload)

            encoded_payload = encoder.encode(decoded_message)

            redecoded_message = decoder.decode(header, encoded_payload)

            assert decoded_message == redecoded_message
