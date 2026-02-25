import pytest

from shine2mqtt.growatt.protocol.base.message import MBAPHeader
from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.set_config.encoder import SetConfigRequestPayloadEncoder
from shine2mqtt.growatt.protocol.set_config.set_config import GrowattSetConfigRequestMessage

DATALOGGER_SERIAL = "XGDABCDEFG"


class TestSetConfigRequestPayloadEncoder:
    @pytest.fixture
    def encoder(self):
        return SetConfigRequestPayloadEncoder()

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
            value="TestString",
        )

        payload = encoder.encode(message)

        expected = b"XGDABCDEFG" + b"\x00" * 20 + b"\x00\x08\x00\x0aTestString"
        assert payload == expected
