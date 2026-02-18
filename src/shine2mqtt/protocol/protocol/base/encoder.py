import struct
from abc import ABC, abstractmethod

from shine2mqtt.protocol.protocol.base.message import BaseMessage


class ByteEncoder:
    @staticmethod
    def encode_bool(value: bool) -> bytes:
        return struct.pack(">B", 1 if value else 0)

    @staticmethod
    def encode_u8(value: int) -> bytes:
        return struct.pack(">B", value)

    @staticmethod
    def encode_u16(value: int) -> bytes:
        return struct.pack(">H", value)

    @staticmethod
    def encode_u32(value: int) -> bytes:
        return struct.pack(">I", value)

    @staticmethod
    def encode_str(value: str, length: int) -> bytes:
        return struct.pack(f">{length}s", value.encode("ascii"))

    @staticmethod
    def set_bit(value: int, bit_index: int, bit_value: bool) -> int:
        if bit_value:
            return value | (1 << bit_index)
        else:
            return value & ~(1 << bit_index)


class PayloadEncoder[T: BaseMessage](ABC, ByteEncoder):
    def __init__(self, message_type: type[T]):
        self.message_type = message_type

    @abstractmethod
    def encode(self, message: T) -> bytes:
        pass
