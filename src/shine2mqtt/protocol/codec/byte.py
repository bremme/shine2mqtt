import struct


class ByteDecoder:
    @staticmethod
    def decode_bool(frame: bytes, offset: int) -> bool:
        return struct.unpack_from(">B", frame, offset)[0] == 1

    @staticmethod
    def decode_u8(frame: bytes, offset: int) -> int:
        return struct.unpack_from(">B", frame, offset)[0]

    @staticmethod
    def decode_u16(frame: bytes, offset: int) -> int:
        return struct.unpack_from(">H", frame, offset)[0]

    @staticmethod
    def decode_u32(frame: bytes, offset: int) -> int:
        return struct.unpack_from(">I", frame, offset)[0]

    @staticmethod
    def decode_str(frame: bytes, offset: int, length: int) -> str:
        return struct.unpack_from(f">{length}s", frame, offset)[0].decode("ascii").strip()

    @staticmethod
    def get_bit(value: int, bit_position: int) -> bool:
        return bool(value & (1 << bit_position))


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
