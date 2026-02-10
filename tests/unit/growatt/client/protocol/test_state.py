import pytest

from shine2mqtt.growatt.client.protocol.state import ClientProtocolSessionState
from shine2mqtt.growatt.protocol.ack.ack import GrowattAckMessage
from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.header.header import MBAPHeader


class TestClientProtocolSessionState:
    @pytest.fixture
    def state(self) -> ClientProtocolSessionState:
        return ClientProtocolSessionState(
            protocol_id=1,
            unit_id=1,
            datalogger_serial="ABC1234567",
        )

    @pytest.fixture
    def ack_message(self) -> GrowattAckMessage:
        return GrowattAckMessage(
            MBAPHeader(
                transaction_id=1,
                protocol_id=1,
                length=1,
                unit_id=1,
                function_code=FunctionCode.ANNOUNCE,
            ),
            ack=True,
        )

    @pytest.fixture
    def nack_message(self) -> GrowattAckMessage:
        return GrowattAckMessage(
            MBAPHeader(
                transaction_id=1,
                protocol_id=1,
                length=1,
                unit_id=1,
                function_code=FunctionCode.ANNOUNCE,
            ),
            ack=False,
        )

    @pytest.mark.parametrize("function_code", list(FunctionCode))
    def test_initial_state(self, state, function_code):
        assert state.protocol_id == 1
        assert state.unit_id == 1
        assert state.datalogger_serial == "ABC1234567"
        assert state.is_announced() is False
        assert state.get_last_send(function_code) is None
        assert state.get_next_transaction_id(function_code) == 1

    def test_update_last_send_stores_timestamp(self, state):
        state.update_last_send(FunctionCode.PING, 123.45)

        assert state.get_last_send(FunctionCode.PING) == pytest.approx(123.45)

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

    def test_announce_sets_announced_when_ack_true(self, state, ack_message):
        state.announce(ack_message)

        assert state.is_announced() is True

    def test_announce_keeps_unannounced_when_ack_false(self, state, nack_message):
        state.announce(nack_message)

        assert state.is_announced() is False

    def test_set_incoming_transaction_id_updates_value(self, state):
        header = MBAPHeader(
            transaction_id=42, protocol_id=1, length=10, unit_id=1, function_code=FunctionCode.PING
        )

        state.set_incoming_transaction_id(header)

        assert state.get_next_transaction_id(FunctionCode.PING) == 43
