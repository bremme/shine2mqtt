import time
from unittest.mock import patch

import pytest

from shine2mqtt.util.clock import MonotonicClockService, has_interval_elapsed


class TestMonotonicClockService:
    def test_now_returns_float(self):
        service = MonotonicClockService()
        result = service.now()
        assert isinstance(result, float)

    def test_now_returns_monotonic_time(self):
        service = MonotonicClockService()
        with patch("time.monotonic", return_value=123.456):
            result = service.now()
        assert result == 123.456

    def test_now_increases_monotonically(self):
        service = MonotonicClockService()
        first = service.now()
        time.sleep(0.001)
        second = service.now()
        assert second > first


@pytest.mark.parametrize(
    "now,last_time,interval,expected",
    [
        (10.0, 0.0, 5, True),
        (10.0, 0.0, 10, True),
        (10.0, 0.0, 11, False),
        (5.5, 2.0, 3, True),
        (5.4, 2.0, 3, True),
        (4.9, 2.0, 3, False),
        (100.0, 100.0, 0, True),
        (100.1, 100.0, 0, True),
    ],
)
def test_has_interval_elapsed_returns_expected(now, last_time, interval, expected):
    result = has_interval_elapsed(now, last_time, interval)
    assert result == expected
