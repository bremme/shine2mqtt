import pytest

from shine2mqtt.growatt.protocol.config import ConfigRegistry
from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.decoders.config import SetConfigRequestDecoder
from shine2mqtt.growatt.protocol.messages.header import MBAPHeader

DATALOGGER_SERIAL = "XGDABCDEFG"


class TestSetConfigRequestDecoder:
    @pytest.fixture
    def decoder(self):
        return SetConfigRequestDecoder(ConfigRegistry())

    def test_decode_set_config_request_known_string_register_success(self, decoder):
        header = MBAPHeader(
            transaction_id=2,
            protocol_id=6,
            length=44,
            unit_id=1,
            function_code=FunctionCode.SET_CONFIG,
        )
        payload = b"XGDABCDEFG" + b"\x00" * 20 + b"\x00\x04\x00\x0a" + b"TestString"

        message = decoder.decode(header, payload)

        assert message.header == header
        assert message.datalogger_serial == DATALOGGER_SERIAL
        assert message.register == 4
        assert message.length == 10
        assert message.value == "TestString"

    def test_decode_set_config_request_unknown_register_returns_string(self, decoder):
        header = MBAPHeader(
            transaction_id=2,
            protocol_id=6,
            length=36,
            unit_id=1,
            function_code=FunctionCode.SET_CONFIG,
        )
        payload = b"XGDABCDEFG" + b"\x00" * 20 + b"\x03\xe8\x00\x02\x00\x2a"

        message = decoder.decode(header, payload)

        assert message.header == header
        assert message.datalogger_serial == DATALOGGER_SERIAL
        assert message.register == 1000
        assert message.length == 2
        assert message.value == "\x00*"

    def test_decode_set_config_request_different_register_success(self, decoder):
        header = MBAPHeader(
            transaction_id=3,
            protocol_id=6,
            length=50,
            unit_id=1,
            function_code=FunctionCode.SET_CONFIG,
        )
        payload = b"XGDABCDEFG" + b"\x00" * 20 + b"\x00\x38\x00\x10" + b"MyWiFiNetwork123"

        message = decoder.decode(header, payload)

        assert message.header == header
        assert message.datalogger_serial == DATALOGGER_SERIAL
        assert message.register == 56
        assert message.length == 16
        assert message.value == "MyWiFiNetwork123"
