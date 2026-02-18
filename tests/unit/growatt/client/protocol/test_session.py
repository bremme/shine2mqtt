from unittest.mock import Mock

import pytest

from shine2mqtt.protocol.client.protocol.session import (
    ClientProtocolSession,
    SendIntervals,
    SendMessageAction,
)
from shine2mqtt.protocol.protocol.constants import FunctionCode


class TestClientProtocolSession:
    @pytest.fixture
    def stub_decoder(self):
        return Mock()

    @pytest.fixture
    def mock_session_state(self):
        state = Mock()
        state.is_announced.return_value = False
        state.get_last_send.return_value = 0.0
        state.get_next_transaction_id.return_value = 1
        return state

    @pytest.fixture
    def stub_clock(self):
        clock = Mock()
        clock.now.return_value = 0.0
        return clock

    @pytest.fixture
    def mock_generator(self):
        generator = Mock()
        generator.generate_frame.return_value = b"test_frame"
        return generator

    @pytest.fixture
    def stub_message_handler(self):
        return Mock()

    @pytest.fixture
    def send_intervals(self) -> SendIntervals:
        return SendIntervals(announce=60, data=300, ping=120)

    @pytest.fixture
    def session(
        self,
        stub_decoder,
        mock_session_state,
        stub_clock,
        mock_generator,
        stub_message_handler,
        send_intervals,
    ) -> ClientProtocolSession:
        return ClientProtocolSession(
            decoder=stub_decoder,
            session_state=mock_session_state,
            clock=stub_clock,
            generator=mock_generator,
            message_handler=stub_message_handler,
            send_intervals=send_intervals,
        )

    def test_handle_incoming_frame_returns_handler_response(self, session, stub_message_handler):
        frame = b"incoming_frame"
        stub_message_handler.handle_message.return_value = b"response_frame"

        result = session.handle_incoming_frame(frame)

        assert result == b"response_frame"

    def test_handle_incoming_frame_returns_none_when_handler_has_no_response(
        self, session, stub_message_handler
    ):
        frame = b"incoming_frame"
        stub_message_handler.handle_message.return_value = None

        result = session.handle_incoming_frame(frame)

        assert result is None

    @pytest.mark.parametrize(
        "function_code",
        [
            FunctionCode.ANNOUNCE,
            FunctionCode.DATA,
            FunctionCode.PING,
        ],
    )
    def test_get_send_message_frame_returns_frame(self, session, function_code):
        action = SendMessageAction(function_code=function_code)

        result = session.get_send_message_frame(action)

        assert result == b"test_frame"
        session.generator.generate_frame.assert_called_once_with(
            transaction_id=1, function_code=function_code
        )
        session.session_state.update_last_send.assert_called_once_with(function_code, 0.0)

    @pytest.mark.parametrize(
        "function_code",
        [
            FunctionCode.BUFFERED_DATA,
            FunctionCode.GET_CONFIG,
            FunctionCode.SET_CONFIG,
        ],
    )
    def test_get_send_message_frame_unknown_message_returns_none(self, session, function_code):
        action = SendMessageAction(function_code=function_code)

        result = session.get_send_message_frame(action)

        assert result is None

    @pytest.mark.parametrize(
        "announced,last_announced_send,last_data_send,last_ping_send,current_time,expected_function_codes",
        [
            # NOT announced, interval elapsed -> ANNOUNCE
            (False, None, None, None, 61.0, [FunctionCode.ANNOUNCE]),
            # NOT announced, interval not elapsed -> ANNOUNCE
            (False, None, None, None, 59.0, [FunctionCode.ANNOUNCE]),
            # NOT announced, last send time is 0, interval not elapsed -> []
            (False, 0.0, None, None, 59.0, []),
            # NOT announced, last send time is 0, interval elapsed -> ANNOUNCE
            (False, 0.0, None, None, 61.0, [FunctionCode.ANNOUNCE]),
            # announced and ping and data never sent -> DATA and PING
            (True, None, None, None, 0.0, [FunctionCode.DATA, FunctionCode.PING]),
            # announced and ping interval elapsed but not data -> PING
            (True, 0.0, 0.0, None, 121.0, [FunctionCode.PING]),
            # announced and ping and data interval elapsed -> DATA and PING
            (True, 0.0, 0.0, 0.0, 301.0, [FunctionCode.DATA, FunctionCode.PING]),
        ],
    )
    def test_get_pending_actions(
        self,
        session: ClientProtocolSession,
        mock_session_state: Mock,
        stub_clock: Mock,
        announced,
        last_announced_send,
        last_data_send,
        last_ping_send,
        current_time,
        expected_function_codes,
    ):
        mock_session_state.is_announced.return_value = announced
        last_send = {
            FunctionCode.ANNOUNCE: last_announced_send,
            FunctionCode.DATA: last_data_send,
            FunctionCode.PING: last_ping_send,
        }
        mock_session_state.get_last_send.side_effect = lambda fc: last_send[fc]
        stub_clock.now.return_value = current_time
        actions = session.get_pending_actions()

        expected_actions = [SendMessageAction(fc) for fc in expected_function_codes]

        assert actions == expected_actions
