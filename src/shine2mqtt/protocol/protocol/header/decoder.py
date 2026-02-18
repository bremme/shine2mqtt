from shine2mqtt.protocol.protocol.base.decoder import ByteDecoder
from shine2mqtt.protocol.protocol.constants import FunctionCode
from shine2mqtt.protocol.protocol.header.header import MBAPHeader


class HeaderDecoder(ByteDecoder):
    def decode(self, frame: bytes) -> MBAPHeader:
        transaction_id = self.decode_u16(frame, 0)
        protocol_id = self.decode_u16(frame, 2)
        length = self.decode_u16(frame, 4)
        unit_id = self.decode_u8(frame, 6)
        function_code = FunctionCode(self.decode_u8(frame, 7))

        return MBAPHeader(
            transaction_id=transaction_id,
            protocol_id=protocol_id,
            length=length,
            unit_id=unit_id,
            function_code=function_code,
        )
