import pytest

from shine2mqtt.protocol.frame.header.encoder import HeaderEncoder
from shine2mqtt.protocol.frame.header.header import FunctionCode, MBAPHeader


class TestHeaderEncoder:
    @pytest.fixture
    def encoder(self):
        return HeaderEncoder()

    def test_encode_header_returns_8_bytes(self, encoder):
        header = MBAPHeader(
            transaction_id=0x0001,
            protocol_id=0x0006,
            length=0x000E,
            unit_id=0x01,
            function_code=FunctionCode.PING,
        )

        result = encoder.encode(header)

        assert len(result) == 8

    def test_encode_header_with_all_fields(self, encoder):
        header = MBAPHeader(
            transaction_id=0x1234,
            protocol_id=0x0006,
            length=0x0014,
            unit_id=0x01,
            function_code=FunctionCode.DATA,
        )

        result = encoder.encode(header)

        assert result == b"\x12\x34\x00\x06\x00\x14\x01\x04"

    def test_encode_header_preserves_transaction_id(self, encoder):
        header = MBAPHeader(
            transaction_id=0xABCD,
            protocol_id=0x0006,
            length=0x000E,
            unit_id=0x01,
            function_code=FunctionCode.ANNOUNCE,
        )

        result = encoder.encode(header)

        assert result[0:2] == b"\xab\xcd"
