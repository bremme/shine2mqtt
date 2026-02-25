def int2hex_string(value: int) -> str:
    return f"{value:02x}"


def bytes2int(value: bytes, size: int = 2) -> list[int] | int:
    integers = []
    for i in range(0, len(value), size):
        chunk = value[i : i + size]
        integers.append(int.from_bytes(chunk, byteorder="big"))
    return integers[0] if len(integers) == 1 else integers
