from datetime import datetime

import pytest

from shine2mqtt.protocol.protocol.announce.announce import GrowattAnnounceMessage, SafetyFunction
from shine2mqtt.protocol.protocol.constants import FunctionCode
from shine2mqtt.protocol.protocol.header.header import MBAPHeader
from shine2mqtt.protocol.server.protocol.session.state import ServerProtocolSessionState

# TEMP
default_function_codes = [
    FunctionCode.ANNOUNCE,
    FunctionCode.PING,
    FunctionCode.DATA,
    FunctionCode.BUFFERED_DATA,
    FunctionCode.SET_CONFIG,
    FunctionCode.GET_CONFIG,
]


class TestServerProtocolSessionState:
    @pytest.fixture
    def state(self) -> ServerProtocolSessionState:
        return ServerProtocolSessionState(
            protocol_id=1,
            unit_id=1,
            datalogger_serial="ABC1234567",
        )

    @pytest.fixture
    def announce_message(self) -> GrowattAnnounceMessage:
        return GrowattAnnounceMessage(
            MBAPHeader(
                transaction_id=1,
                protocol_id=1,
                length=1,
                unit_id=1,
                function_code=FunctionCode.ANNOUNCE,
            ),
            datalogger_serial="DATALOGGER_SERIAL",
            inverter_serial="INVERTER_SERIAL",
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
        )

    @pytest.mark.parametrize("function_code", default_function_codes)
    def test_initial_state(self, state, function_code):
        assert state.protocol_id == 1
        assert state.unit_id == 1
        assert state.datalogger_serial == "ABC1234567"
        assert state.is_announced() is False
        assert state.get_next_transaction_id(function_code) == 1

    def test_get_next_transaction_id_increments(self, state):
        first = state.get_next_transaction_id(FunctionCode.ANNOUNCE)
        second = state.get_next_transaction_id(FunctionCode.ANNOUNCE)

        assert second == first + 1

    def test_get_next_transaction_id_independent_per_function_code(self, state):
        state.get_next_transaction_id(FunctionCode.ANNOUNCE)

        ping_id = state.get_next_transaction_id(FunctionCode.PING)
        announce_id = state.get_next_transaction_id(FunctionCode.ANNOUNCE)
        data_id = state.get_next_transaction_id(FunctionCode.DATA)
        buffered_data_id = state.get_next_transaction_id(FunctionCode.BUFFERED_DATA)
        set_config_id = state.get_next_transaction_id(FunctionCode.SET_CONFIG)
        get_config_id = state.get_next_transaction_id(FunctionCode.GET_CONFIG)

        assert announce_id != data_id
        assert announce_id != ping_id
        assert announce_id != buffered_data_id
        assert announce_id != set_config_id
        assert announce_id != get_config_id

    def test_announce_sets_announced_when_ack_true(self, state, announce_message):
        state.announce(announce_message)

        assert state.is_announced() is True
        assert state.protocol_id == 1
        assert state.unit_id == 1
        assert state.datalogger_serial == "DATALOGGER_SERIAL"

    def test_set_incoming_transaction_id_updates_value(self, state):
        header = MBAPHeader(
            transaction_id=42, protocol_id=1, length=10, unit_id=1, function_code=FunctionCode.PING
        )

        state.set_incoming_transaction_id(header)

        assert state.get_next_transaction_id(FunctionCode.PING) == 43
