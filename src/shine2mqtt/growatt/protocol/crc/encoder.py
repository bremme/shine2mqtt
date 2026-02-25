import struct


class CRCEncoder:
    @staticmethod
    def encode(crc: int) -> bytes:
        # NOTE: CRC is little-endian
        return struct.pack("<H", crc)
