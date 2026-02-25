def u16_to_bytes(value: int) -> bytes:
    if value < 0:
        raise ValueError("Only unsigned 16 bit integers are allowed")
    if value > 0xFFFF:
        raise ValueError(f"Value exceeds maximum ({0xFFFF}) for unsigned 16 bit integer")
    return value.to_bytes(2, byteorder="big")


def u16_to_hex_string(value: int) -> str:
    byte_value = u16_to_bytes(value)
    return byte_value.hex().upper()


def hex_string_to_u16(hex_string: str) -> int:
    sanitized_hex_string = hex_string.replace(" ", "").replace("0x", "")
    if len(sanitized_hex_string) > 4:
        raise ValueError("Hex string must be at most 4 characters long for unsigned 16 bit integer")
    byte_value = bytes.fromhex(sanitized_hex_string)
    return int.from_bytes(byte_value, byteorder="big")


def bytes_to_int(value: bytes) -> list[int]:
    integers = []
    for i in range(0, len(value), 2):
        chunk = value[i : i + 2]
        integers.append(int.from_bytes(chunk, byteorder="big"))
    return integers


def bytes_to_u16(value: bytes) -> int:
    return bytes_to_int(value)[0]
