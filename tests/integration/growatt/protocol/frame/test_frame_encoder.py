import pytest

from shine2mqtt.protocol.protocol.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.protocol.base.message import BaseMessage
from shine2mqtt.protocol.protocol.constants import FunctionCode
from shine2mqtt.protocol.protocol.frame.encoder import FrameEncoder
from shine2mqtt.protocol.protocol.get_config.get_config import (
    GrowattGetConfigRequestMessage,
)
from shine2mqtt.protocol.protocol.header.header import MBAPHeader
from shine2mqtt.protocol.protocol.ping.message import GrowattPingMessage
from shine2mqtt.protocol.protocol.set_config.set_config import (
    GrowattSetConfigRequestMessage,
)

ENCRYPTION_KEY = b"Growatt"

MESSAGES = [
    GrowattPingMessage(
        header=MBAPHeader(
            transaction_id=2,
            protocol_id=6,
            length=0,
            unit_id=1,
            function_code=FunctionCode.PING,
        ),
        datalogger_serial="XGD4A49AGC",
    ),
    GrowattGetConfigRequestMessage(
        header=MBAPHeader(
            transaction_id=2,
            protocol_id=6,
            length=0,
            unit_id=1,
            function_code=FunctionCode.GET_CONFIG,
        ),
        datalogger_serial="XGD4A49AGC",
        register_start=0,
        register_end=10,
    ),
    GrowattSetConfigRequestMessage(
        header=MBAPHeader(
            transaction_id=2,
            protocol_id=6,
            length=0,
            unit_id=1,
            function_code=FunctionCode.SET_CONFIG,
        ),
        datalogger_serial="XGD4A49AGC",
        register=5,
        value="42",
    ),
    GrowattAckMessage(
        header=MBAPHeader(
            transaction_id=2,
            protocol_id=6,
            length=0,
            unit_id=1,
            function_code=FunctionCode.DATA,
        ),
        ack=True,
    ),
]

FRAMES = [
    b"\x00\x02\x00\x06\x00\x0c\x01\x16\x1f5+C @M\x065,\x15|",
    b"\x00\x02\x00\x06\x00\x10\x01\x19\x1f5+C @M\x065,wat~\xdcb",
    b"\x00\x02\x00\x06\x00&\x01\x18\x1f5+C @M\x065,wattGrowattGrowattGrorav@u/3",
    b"\x00\x02\x00\x06\x00\x03\x01\x04G9\x98",
]

CASES = [
    (MESSAGES[0], FRAMES[0]),
    (MESSAGES[1], FRAMES[1]),
    (MESSAGES[2], FRAMES[2]),
    (MESSAGES[3], FRAMES[3]),
]


class TestFrameEncoder:
    @pytest.fixture
    def encoder(self):
        from shine2mqtt.protocol.protocol.frame import FrameFactory

        return FrameFactory.encoder()

    @pytest.mark.parametrize("message,expected_frame", CASES, ids=list(range(len(CASES))))
    def test_encode_valid_message_success(
        self,
        encoder: FrameEncoder,
        message: BaseMessage,
        expected_frame: bytes,
    ):
        frame = encoder.encode(message)

        assert frame == expected_frame
