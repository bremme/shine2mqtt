from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.decoders.decoder import ByteDecoder
from shine2mqtt.growatt.protocol.messages.base import MBAPHeader


class HeaderDecoder(ByteDecoder):
    @staticmethod
    def decode(frame: bytes) -> MBAPHeader:
        transaction_id = HeaderDecoder.decode_u16(frame, 0)

        protocol_id = HeaderDecoder.decode_u16(frame, 2)
        length = HeaderDecoder.decode_u16(frame, 4)
        unit_id = HeaderDecoder.decode_u8(frame, 6)
        function_code = FunctionCode(HeaderDecoder.decode_u8(frame, 7))

        return MBAPHeader(
            transaction_id=transaction_id,
            protocol_id=protocol_id,
            length=length,
            unit_id=unit_id,
            function_code=function_code,
        )
