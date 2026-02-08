from shine2mqtt.growatt.protocol.encoders.crc import CRCEncoder


class TestCRCEncoder:
    def test_encode_crc_returns_little_endian_bytes(self):
        result = CRCEncoder.encode(0x1234)

        assert result == b"\x34\x12"

    def test_encode_crc_zero(self):
        result = CRCEncoder.encode(0x0000)

        assert result == b"\x00\x00"

    def test_encode_crc_max_value(self):
        result = CRCEncoder.encode(0xFFFF)

        assert result == b"\xff\xff"
