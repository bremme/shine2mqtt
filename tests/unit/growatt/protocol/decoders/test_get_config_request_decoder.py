import pytest

from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.decoders.get_config import GetConfigRequestDecoder
from shine2mqtt.growatt.protocol.messages.header import MBAPHeader

DATALOGGER_SERIAL = "XGDABCDEFG"


class TestGetConfigRequestDecoder:
    @pytest.fixture
    def decoder(self):
        return GetConfigRequestDecoder()

    def test_decode_get_config_request_valid_payload_success(self, decoder):
        header = MBAPHeader(
            transaction_id=2,
            protocol_id=6,
            length=14,
            unit_id=1,
            function_code=FunctionCode.GET_CONFIG,
        )
        payload = b"XGDABCDEFG\x00\x00\x00\x0a"

        message = decoder.decode(header, payload)

        assert message.header == header
        assert message.datalogger_serial == DATALOGGER_SERIAL
        assert message.register_start == 0
        assert message.register_end == 10

    def test_decode_get_config_request_different_range_success(self, decoder):
        header = MBAPHeader(
            transaction_id=3,
            protocol_id=6,
            length=14,
            unit_id=1,
            function_code=FunctionCode.GET_CONFIG,
        )
        payload = b"XGDABCDEFG\x00\x14\x00\x28"

        message = decoder.decode(header, payload)

        assert message.header == header
        assert message.datalogger_serial == DATALOGGER_SERIAL
        assert message.register_start == 20
        assert message.register_end == 40
