from shine2mqtt.protocol.messages.encoder.encoder import PayloadEncoder
from shine2mqtt.protocol.messages.read_register.read_register import (
    GrowattReadMultipleRegistersRequestMessage,
)


class ReadRegistersPayloadEncoder(PayloadEncoder[GrowattReadMultipleRegistersRequestMessage]):
    def __init__(self):
        super().__init__(GrowattReadMultipleRegistersRequestMessage)

    def encode(self, message: GrowattReadMultipleRegistersRequestMessage) -> bytes:
        payload = bytearray(34)
        payload[0:10] = self.encode_str(message.datalogger_serial, 10)
        payload[10:30] = b"\x00" * 20
        payload[30:32] = self.encode_u16(message.register_start)
        payload[32:34] = self.encode_u16(message.register_end)
        return bytes(payload)
