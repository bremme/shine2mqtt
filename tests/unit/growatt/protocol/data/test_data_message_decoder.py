from datetime import datetime

import pytest

from shine2mqtt.growatt.protocol.constants import InverterStatus
from shine2mqtt.growatt.protocol.data.data import GrowattDataMessage
from shine2mqtt.growatt.protocol.data.decoder import DataRequestDecoder
from tests.utils.loader import CapturedFrameLoader

frames, headers, payloads = CapturedFrameLoader.load("data_message")

DATALOGGER_SERIAL = "XGDABCDEFG"
INVERTER_SERIAL = "MLG0A12345"

EXPECTED_MESSAGES = [
    GrowattDataMessage(
        header=headers[0],
        datalogger_serial=DATALOGGER_SERIAL,
        inverter_serial=INVERTER_SERIAL,
        timestamp=datetime(2026, 1, 12, 11, 27),
        inverter_status=InverterStatus.NORMAL,
        power_dc=201.7,
        voltage_dc_1=315.5,
        current_dc_1=0.6,
        power_dc_1=201.7,
        voltage_dc_2=0.0,
        current_dc_2=0.0,
        power_dc_2=0.0,
        power_ac=197.7,
        frequency_ac=50.02,
        voltage_ac_1=231.0,
        current_ac_1=1.4,
        power_ac_1=198.2,
        voltage_ac_l1_l2=231.0,
        voltage_ac_l2_l3=0.0,
        voltage_ac_l3_l1=0.0,
        total_run_time=40012,
        energy_ac_today=0.0,
        energy_ac_total=7456.1,
        energy_dc_1_today=0.0,
        energy_dc_1_total=7532.4,
        energy_dc_2_today=0.0,
        energy_dc_2_total=0.0,
        energy_dc_total=7532.4,
        temperature=25.9,
    ),
    GrowattDataMessage(
        header=headers[1],
        datalogger_serial=DATALOGGER_SERIAL,
        inverter_serial=INVERTER_SERIAL,
        timestamp=datetime(2026, 1, 12, 11, 27),
        inverter_status=InverterStatus.NORMAL,
        power_dc=203.3,
        voltage_dc_1=327.3,
        current_dc_1=0.6,
        power_dc_1=203.3,
        voltage_dc_2=0.0,
        current_dc_2=0.0,
        power_dc_2=0.0,
        power_ac=199.5,
        frequency_ac=50.03,
        voltage_ac_1=231.1,
        current_ac_1=1.5,
        power_ac_1=199.4,
        voltage_ac_l1_l2=231.1,
        voltage_ac_l2_l3=0.0,
        voltage_ac_l3_l1=0.0,
        total_run_time=40012,
        energy_ac_today=0.0,
        energy_ac_total=7456.1,
        energy_dc_1_today=0.0,
        energy_dc_1_total=7532.4,
        energy_dc_2_today=0.0,
        energy_dc_2_total=0.0,
        energy_dc_total=7532.4,
        temperature=26.1,
    ),
]

CASES = list(zip(headers[:2], payloads[:2], EXPECTED_MESSAGES, strict=True))


class TestDataRequestDecoder:
    @pytest.fixture
    def decoder(self):
        return DataRequestDecoder()

    @pytest.mark.parametrize(
        "header,payload,expected", CASES, ids=[f"{i}" for i in range(len(CASES))]
    )
    def test_decode_data_request_valid_header_and_payload_success(
        self, decoder, header, payload, expected
    ):
        message = decoder.decode(header, payload)

        assert message == expected
