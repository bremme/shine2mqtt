from shine2mqtt.growatt.protocol.encoders.encoder import ByteEncoder
from shine2mqtt.growatt.protocol.messages.base import MBAPHeader


class HeaderEncoder(ByteEncoder):
    def encode(self, header: MBAPHeader) -> bytes:
        raw_header = self.encode_u16(header.transaction_id)
        raw_header += self.encode_u16(header.protocol_id)
        raw_header += self.encode_u16(header.length)
        raw_header += self.encode_u8(header.unit_id)
        raw_header += self.encode_u8(header.function_code.value)
        return raw_header
