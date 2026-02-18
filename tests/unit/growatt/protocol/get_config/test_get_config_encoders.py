import pytest

from shine2mqtt.protocol.protocol.constants import FunctionCode
from shine2mqtt.protocol.protocol.get_config.encoder import (
    GetConfigRequestPayloadEncoder,
    GetConfigResponsePayloadEncoder,
)
from shine2mqtt.protocol.protocol.get_config.get_config import (
    GrowattGetConfigRequestMessage,
    GrowattGetConfigResponseMessage,
)
from shine2mqtt.protocol.protocol.header.header import MBAPHeader

DATALOGGER_SERIAL = "XGDABCDEFG"


class TestGetConfigRequestPayloadEncoder:
    @pytest.fixture
    def encoder(self):
        return GetConfigRequestPayloadEncoder()

    def test_encode_get_config_request_returns_valid_payload(self, encoder):
        header = MBAPHeader(
            transaction_id=2,
            protocol_id=6,
            length=14,
            unit_id=1,
            function_code=FunctionCode.GET_CONFIG,
        )
        message = GrowattGetConfigRequestMessage(
            header=header,
            datalogger_serial=DATALOGGER_SERIAL,
            register_start=0,
            register_end=10,
        )

        payload = encoder.encode(message)

        assert payload == b"XGDABCDEFG\x00\x00\x00\x0a"

    def test_encode_get_config_request_different_range(self, encoder):
        header = MBAPHeader(
            transaction_id=3,
            protocol_id=6,
            length=14,
            unit_id=1,
            function_code=FunctionCode.GET_CONFIG,
        )
        message = GrowattGetConfigRequestMessage(
            header=header,
            datalogger_serial=DATALOGGER_SERIAL,
            register_start=20,
            register_end=40,
        )

        payload = encoder.encode(message)

        assert payload == b"XGDABCDEFG\x00\x14\x00\x28"


class TestGetConfigResponsePayloadEncoder:
    @pytest.fixture
    def encoder(self):
        return GetConfigResponsePayloadEncoder()

    def test_encode_get_config_response_returns_valid_payload(self, encoder):
        header = MBAPHeader(
            transaction_id=2,
            protocol_id=6,
            length=47,
            unit_id=1,
            function_code=FunctionCode.GET_CONFIG,
        )
        message = GrowattGetConfigResponseMessage(
            header=header,
            datalogger_serial=DATALOGGER_SERIAL,
            register=14,
            data=b"192.168.1.100",
            value="192.168.1.100",
        )

        payload = encoder.encode(message)

        expected = b"XGDABCDEFG" + b"\x00" * 20 + b"\x00\x0e\x00\x0d" + b"192.168.1.100"
        assert payload == expected

    def test_encode_get_config_response_with_different_register(self, encoder):
        header = MBAPHeader(
            transaction_id=3,
            protocol_id=6,
            length=40,
            unit_id=1,
            function_code=FunctionCode.GET_CONFIG,
        )
        message = GrowattGetConfigResponseMessage(
            header=header,
            datalogger_serial=DATALOGGER_SERIAL,
            register=56,
            data=b"MySSID",
            value="MySSID",
        )

        payload = encoder.encode(message)

        expected = b"XGDABCDEFG" + b"\x00" * 20 + b"\x00\x38\x00\x06" + b"MySSID"
        assert payload == expected
