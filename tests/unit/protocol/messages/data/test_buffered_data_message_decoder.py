from datetime import datetime

import pytest

from shine2mqtt.protocol.messages.data.data import GrowattDataMessage, InverterStatus
from shine2mqtt.protocol.messages.data.decoder import BufferDataRequestDecoder
from tests.utils.loader import CapturedFrameLoader

frames, headers, payloads = CapturedFrameLoader.load("buffered_data_message")

DATALOGGER_SERIAL = "XGDABCDEFG"
INVERTER_SERIAL = "MLG0A12345"

EXPECTED_MESSAGES = [
    GrowattDataMessage(
        header=headers[0],
        datalogger_serial=DATALOGGER_SERIAL,
        inverter_serial=INVERTER_SERIAL,
        timestamp=datetime(2026, 1, 12, 11, 27),
        inverter_status=InverterStatus.NORMAL,
        power_dc=276.4,
        voltage_dc_1=325.9,
        current_dc_1=0.8,
        power_dc_1=276.4,
        voltage_dc_2=0.0,
        current_dc_2=0.0,
        power_dc_2=0.0,
        power_ac=271.0,
        frequency_ac=49.99,
        voltage_ac_1=233.7,
        current_ac_1=1.5,
        power_ac_1=272.5,
        voltage_ac_l1_l2=233.7,
        voltage_ac_l2_l3=0.0,
        voltage_ac_l3_l1=0.0,
        total_run_time=39822,
        energy_ac_today=0.2,
        energy_ac_total=7440.9,
        energy_dc_1_today=0.2,
        energy_dc_1_total=7517.1,
        energy_dc_2_today=0.0,
        energy_dc_2_total=0.0,
        energy_dc_total=7517.1,
        temperature=32.1,
    ),
]

CASES = list(zip(headers[:1], payloads[:1], EXPECTED_MESSAGES, strict=True))


class TestBufferDataRequestDecoder:
    @pytest.fixture
    def decoder(self):
        return BufferDataRequestDecoder()

    @pytest.mark.parametrize(
        "header,payload,expected", CASES, ids=[f"{i}" for i in range(len(CASES))]
    )
    def test_decode_buffered_data_request_valid_header_and_payload_success(
        self, decoder, header, payload, expected
    ):
        message = decoder.decode(header, payload)

        assert message == expected
