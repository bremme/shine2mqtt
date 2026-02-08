from shine2mqtt.growatt.protocol.encoders.encoder import ByteEncoder


class TestByteEncoder:
    def test_encode_bool_true_returns_one(self):
        result = ByteEncoder.encode_bool(True)

        assert result == b"\x01"

    def test_encode_bool_false_returns_zero(self):
        result = ByteEncoder.encode_bool(False)

        assert result == b"\x00"

    def test_encode_u8_returns_single_byte(self):
        result = ByteEncoder.encode_u8(42)

        assert result == b"\x2a"

    def test_encode_u16_returns_two_bytes_big_endian(self):
        result = ByteEncoder.encode_u16(0x1234)

        assert result == b"\x12\x34"

    def test_encode_u32_returns_four_bytes_big_endian(self):
        result = ByteEncoder.encode_u32(0x12345678)

        assert result == b"\x12\x34\x56\x78"

    def test_encode_str_pads_with_nulls(self):
        result = ByteEncoder.encode_str("hello", 10)

        assert result == b"hello\x00\x00\x00\x00\x00"

    def test_encode_str_truncates_if_too_long(self):
        result = ByteEncoder.encode_str("hello world", 5)

        assert result == b"hello"

    def test_set_bit_sets_bit_to_one(self):
        result = ByteEncoder.set_bit(0b00000000, 3, True)

        assert result == 0b00001000

    def test_set_bit_clears_bit_to_zero(self):
        result = ByteEncoder.set_bit(0b11111111, 3, False)

        assert result == 0b11110111
