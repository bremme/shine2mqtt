from shine2mqtt.growatt.protocol.encoders.encoder import PayloadEncoder
from shine2mqtt.growatt.protocol.messages.config import (
    GrowattGetConfigRequestMessage,
    GrowattGetConfigResponseMessage,
)


class GetConfigRequestPayloadEncoder(PayloadEncoder[GrowattGetConfigRequestMessage]):
    def __init__(self):
        super().__init__(GrowattGetConfigRequestMessage)

    def encode(self, message: GrowattGetConfigRequestMessage) -> bytes:
        payload = self.encode_str(message.datalogger_serial, 10)
        payload += self.encode_u16(message.register_start)
        payload += self.encode_u16(message.register_end)
        return payload


class GetConfigResponsePayloadEncoder(PayloadEncoder[GrowattGetConfigResponseMessage]):
    def __init__(self):
        super().__init__(GrowattGetConfigResponseMessage)

    def encode(self, message: GrowattGetConfigResponseMessage) -> bytes:
        size = 10 + 20 + 2 + 2 + len(message.data)
        payload = bytearray(size)
        payload[0:10] = self.encode_str(message.datalogger_serial, 10)
        # 10-30 is \x00 (padding)
        payload[30:32] = self.encode_u16(message.register)
        payload[32:34] = self.encode_u16(message.length)
        payload[34 : 34 + len(message.data)] = message.data
        return bytes(payload)
