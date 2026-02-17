from datetime import datetime

import pytest

from shine2mqtt.growatt.protocol.announce.announce import GrowattAnnounceMessage, SafetyFunction
from shine2mqtt.growatt.protocol.base.message import BaseMessage
from shine2mqtt.growatt.protocol.constants import InverterStatus
from shine2mqtt.growatt.protocol.data.data import GrowattDataMessage
from shine2mqtt.growatt.protocol.frame.decoder import FrameDecoder
from shine2mqtt.growatt.protocol.frame.factory import FrameFactory
from shine2mqtt.growatt.protocol.get_config.get_config import (
    GrowattGetConfigResponseMessage,
)
from shine2mqtt.growatt.protocol.ping.message import GrowattPingMessage
from shine2mqtt.growatt.protocol.set_config.set_config import GrowattSetConfigResponseMessage
from tests.utils.loader import CapturedFrameLoader

announce_frames, announce_headers, announce_payloads = CapturedFrameLoader.load("announce_message")
buffered_data_frames, buffered_data_headers, buffered_data_payloads = CapturedFrameLoader.load(
    "buffered_data_message"
)
data_frames, data_headers, data_payloads = CapturedFrameLoader.load("data_message")
get_config_frames, get_config_headers, get_config_payloads = CapturedFrameLoader.load(
    "get_config_message"
)
ping_frames, ping_headers, ping_payloads = CapturedFrameLoader.load("ping_message")

set_config_response_frames, set_config_response_headers, set_config_response_payloads = (
    CapturedFrameLoader.load("set_config_response")
)

DECRYPTION_KEY = b"Growatt"
DATALOGGER_SERIAL = "XGDABCDEFG"
INVERTER_SERIAL = "MLG0A12345"


EXPECTED_MESSAGES = [
    GrowattAnnounceMessage(
        header=announce_headers[0],
        datalogger_serial=DATALOGGER_SERIAL,
        inverter_serial=INVERTER_SERIAL,
        remote_on_off=False,
        safety_function=SafetyFunction(
            spi=True,
            auto_test_start=False,
            low_voltage_fault_ride_through=False,
            frequency_derating=True,
            soft_start=True,
            demand_response_management_system=False,
            power_voltage_control=False,
            high_voltage_fault_ride_through=False,
            rate_of_change_of_frequency_protection=False,
            frequency_derating_recovery=False,
        ),
        power_factor_memory=False,
        active_power_ac_max=100,
        reactive_power_ac_max=0,
        power_factor=1.0,
        rated_power_ac=3000.0,
        rated_voltage_dc=100.0,
        inverter_fw_version="GH1.0",
        inverter_control_fw_version="ZAAA.8",
        lcd_language="English",
        device_type="PV Inverter",
        timestamp=datetime(2026, 2, 3, 9, 22, 17),
        voltage_ac_low_limit=184.0,
        voltage_ac_high_limit=264.5,
        frequency_ac_low_limit=47.5,
        frequency_ac_high_limit=51.5,
        power_factor_control_mode="Unity PF",
    ),
    GrowattDataMessage(
        header=buffered_data_headers[0],
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
    GrowattDataMessage(
        header=data_headers[0],
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
    GrowattGetConfigResponseMessage(
        header=get_config_headers[14],
        datalogger_serial=DATALOGGER_SERIAL,
        register=14,
        data=b"192.168.1.100",
        name="ip_address",
        description="Local IP",
        value="192.168.1.100",
    ),
    GrowattSetConfigResponseMessage(
        header=set_config_response_headers[0],
        datalogger_serial=DATALOGGER_SERIAL,
        register=4,
        ack=True,
    ),
    GrowattPingMessage(
        header=ping_headers[0],
        datalogger_serial=DATALOGGER_SERIAL,
    ),
]


CASES = [
    (announce_frames[0], EXPECTED_MESSAGES[0]),
    (buffered_data_frames[0], EXPECTED_MESSAGES[1]),
    (data_frames[0], EXPECTED_MESSAGES[2]),
    (get_config_frames[14], EXPECTED_MESSAGES[3]),
    (set_config_response_frames[0], EXPECTED_MESSAGES[4]),
    (ping_frames[0], EXPECTED_MESSAGES[5]),
]


class TestFrameDecoder:
    @pytest.fixture
    def decoder(self):
        return FrameFactory.server_decoder()

    @pytest.mark.parametrize("frame,expected_message", CASES, ids=list(range(len(CASES))))
    def test_decode_valid_frame_success(
        self,
        decoder: FrameDecoder,
        frame: bytes,
        expected_message: BaseMessage,
    ):
        message = decoder.decode(frame)

        assert message == expected_message
