import struct
from abc import ABC, abstractmethod
from datetime import datetime

from shine2mqtt.protocol.codec.byte import ByteEncoder
from shine2mqtt.protocol.messages.message import BaseMessage


class PayloadEncoder[T: BaseMessage](ABC, ByteEncoder):
    def __init__(self, message_type: type[T]):
        self.message_type = message_type

    @abstractmethod
    def encode(self, message: T) -> bytes:
        pass

    def encode_datetime(self, timestamp: datetime, fmt: str) -> bytes:
        step = 2 if fmt == "H" else 1
        year_offset = 0 if fmt == "H" else 2000

        payload = bytearray(6 * step)
        struct.pack_into(f">{fmt}", payload, 0 * step, timestamp.year - year_offset)
        struct.pack_into(f">{fmt}", payload, 1 * step, timestamp.month)
        struct.pack_into(f">{fmt}", payload, 2 * step, timestamp.day)
        struct.pack_into(f">{fmt}", payload, 3 * step, timestamp.hour)
        struct.pack_into(f">{fmt}", payload, 4 * step, timestamp.minute)
        struct.pack_into(f">{fmt}", payload, 5 * step, timestamp.second)

        return bytes(payload)
