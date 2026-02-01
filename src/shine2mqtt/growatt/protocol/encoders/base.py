import struct
from abc import ABC, abstractmethod

from shine2mqtt.growatt.protocol.messages.base import BaseMessage


class ByteEncoder:
    def encode_bool(self, value: bool) -> bytes:
        return struct.pack(">B", 1 if value else 0)

    def encode_string(self, value: str, length: int) -> bytes:
        return struct.pack(f">{length}s", value.encode("ascii"))

    def encode_uint8(self, value: int) -> bytes:
        return struct.pack(">B", value)

    def encode_uint16(self, value: int) -> bytes:
        return struct.pack(">H", value)

    def encode_uint32(self, value: int) -> bytes:
        return struct.pack(">I", value)

    def set_bit(self, value: int, bit_index: int, bit_value: bool) -> int:
        if bit_value:
            return value | (1 << bit_index)
        else:
            return value & ~(1 << bit_index)


class BaseEncoder[T: BaseMessage](ABC, ByteEncoder):
    def __init__(self, message_type: type[T]):
        self.message_type = message_type

    @abstractmethod
    def encode(self, message: T) -> bytes:
        pass
