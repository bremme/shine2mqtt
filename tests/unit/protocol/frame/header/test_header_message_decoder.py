import pytest

from shine2mqtt.protocol.frame.header.decoder import HeaderDecoder
from tests.utils.loader import CapturedFrameLoader

frames, headers, payloads = CapturedFrameLoader.load("ping_message")


CASES = list(zip(frames[:2], headers[:2], strict=True))


class TestHeaderDecoder:
    @pytest.mark.parametrize(
        "frame,expected_header",
        CASES,
        ids=[f"{i}" for i in range(len(CASES))],
    )
    def test_decode(self, frame, expected_header):
        decoder = HeaderDecoder()
        header = decoder.decode(frame)

        assert header == expected_header
