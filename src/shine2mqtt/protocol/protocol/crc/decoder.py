import struct


class CRCDecoder:
    @staticmethod
    def decode(crc: bytes) -> int:
        # NOTE: CRC is little-endian
        return struct.unpack("<H", crc)[0]
