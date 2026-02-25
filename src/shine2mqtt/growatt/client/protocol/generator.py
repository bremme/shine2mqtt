from itertools import cycle

from shine2mqtt.growatt.client.protocol.loader import CapturedFrameLoader
from shine2mqtt.growatt.protocol.constants import ACK, NACK, FunctionCode
from shine2mqtt.growatt.protocol.frame.encoder import FrameEncoder
from shine2mqtt.growatt.protocol.header.header import MBAPHeader

announce_frames, announce_headers, announce_payloads = CapturedFrameLoader.load("announce_message")
buffered_data_frames, buffered_data_headers, buffered_data_payloads = CapturedFrameLoader.load(
    "buffered_data_message"
)
data_frames, data_headers, data_payloads = CapturedFrameLoader.load("data_message")
get_config_frames, get_config_headers, get_config_payloads = CapturedFrameLoader.load(
    "get_config_response"
)
ping_frames, ping_headers, ping_payloads = CapturedFrameLoader.load("ping_message")


class FrameGenerator:
    def __init__(self, encoder: FrameEncoder):
        self.announce_headers = cycle(announce_headers)
        self.announce_payloads = cycle(announce_payloads)

        self.data_headers = cycle(data_headers)
        self.data_payloads = cycle(data_payloads)

        self.get_config_headers = dict(enumerate(get_config_headers))
        self.get_config_payloads = dict(enumerate(get_config_payloads))

        self.ping_headers = cycle(ping_headers)
        self.ping_payloads = cycle(ping_payloads)

        self.encoder = encoder

    def generate_frame(self, transaction_id: int, function_code: FunctionCode) -> bytes:
        match function_code:
            case FunctionCode.ANNOUNCE:
                return self.generate_announce_frame(transaction_id)
            case FunctionCode.DATA:
                return self.generate_data_frame(transaction_id)
            case FunctionCode.PING:
                return self.generate_ping_frame(transaction_id)
            case _:
                raise NotImplementedError(f"No generator for {function_code}")

    def generate_announce_frame(self, transaction_id: int) -> bytes:
        raw_payload = next(self.announce_payloads)

        header = next(self.announce_headers)
        header.transaction_id = transaction_id

        return self.encoder.encode_frame(header, raw_payload)

    def generate_data_frame(self, transaction_id: int) -> bytes:
        raw_payload = next(self.data_payloads)

        header = next(self.data_headers)
        header.transaction_id = transaction_id

        return self.encoder.encode_frame(header, raw_payload)

    def generate_ping_frame(self, transaction_id: int) -> bytes:
        raw_payload = next(self.ping_payloads)

        header = next(self.ping_headers)
        header.transaction_id = transaction_id

        return self.encoder.encode_frame(header, raw_payload)

    def generate_get_config_response_frame(self, transaction_id: int, register: int) -> bytes:
        raw_payload = self.get_config_payloads.get(register)
        header = self.get_config_headers.get(register)

        if header is None or raw_payload is None:
            raise ValueError(f"Unknown register {register}")

        header.transaction_id = transaction_id

        return self.encoder.encode_frame(header, raw_payload)

    def generate_ack_frame(self, header: MBAPHeader, ack: bool) -> bytes:
        payload = ACK if ack else NACK
        return self.encoder.encode_frame(header, payload)
