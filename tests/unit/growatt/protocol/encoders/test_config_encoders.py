import pytest

from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.encoders.config import (
    GetConfigRequestPayloadEncoder,
    GetConfigResponsePayloadEncoder,
    SetConfigRequestPayloadEncoder,
)
from shine2mqtt.growatt.protocol.messages.base import MBAPHeader
from shine2mqtt.growatt.protocol.messages.config import (
    GrowattGetConfigRequestMessage,
    GrowattGetConfigResponseMessage,
    GrowattSetConfigRequestMessage,
)

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


class TestSetConfigRequestPayloadEncoder:
    @pytest.fixture
    def encoder(self):
        return SetConfigRequestPayloadEncoder()

    def test_encode_set_config_request_with_int_value(self, encoder):
        header = MBAPHeader(
            transaction_id=2,
            protocol_id=6,
            length=16,
            unit_id=1,
            function_code=FunctionCode.SET_CONFIG,
        )
        message = GrowattSetConfigRequestMessage(
            header=header,
            datalogger_serial=DATALOGGER_SERIAL,
            register=5,
            length=2,
            value=42,
        )

        payload = encoder.encode(message)

        assert payload == b"XGDABCDEFG\x00\x05\x00\x02\x00\x2a"

    def test_encode_set_config_request_with_string_value(self, encoder):
        header = MBAPHeader(
            transaction_id=3,
            protocol_id=6,
            length=24,
            unit_id=1,
            function_code=FunctionCode.SET_CONFIG,
        )
        message = GrowattSetConfigRequestMessage(
            header=header,
            datalogger_serial=DATALOGGER_SERIAL,
            register=8,
            length=10,
            value="TestString",
        )

        payload = encoder.encode(message)

        assert payload == b"XGDABCDEFG\x00\x08\x00\x0aTestString"


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
            length=13,
            data=b"192.168.1.100",
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
            length=6,
            data=b"MySSID",
        )

        payload = encoder.encode(message)

        expected = b"XGDABCDEFG" + b"\x00" * 20 + b"\x00\x38\x00\x06" + b"MySSID"
        assert payload == expected
