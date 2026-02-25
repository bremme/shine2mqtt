from shine2mqtt.growatt.protocol.base.encoder import PayloadEncoder
from shine2mqtt.growatt.protocol.get_config.get_config import (
    GrowattGetConfigRequestMessage,
    GrowattGetConfigResponseMessage,
)


class GetConfigRequestPayloadEncoder(PayloadEncoder[GrowattGetConfigRequestMessage]):
    def __init__(self):
        super().__init__(GrowattGetConfigRequestMessage)

    def encode(self, message: GrowattGetConfigRequestMessage) -> bytes:
        payload = bytearray(14)
        payload[0:10] = self.encode_str(message.datalogger_serial, 10)
        payload[10:12] = self.encode_u16(message.register_start)
        payload[12:14] = self.encode_u16(message.register_end)
        return bytes(payload)


class GetConfigResponsePayloadEncoder(PayloadEncoder[GrowattGetConfigResponseMessage]):
    def __init__(self):
        super().__init__(GrowattGetConfigResponseMessage)

    def encode(self, message: GrowattGetConfigResponseMessage) -> bytes:
        length = len(message.data)

        size = 10 + 20 + 2 + 2 + length
        payload = bytearray(size)
        payload[0:10] = self.encode_str(message.datalogger_serial, 10)
        # 10-30 is \x00 (padding)
        payload[30:32] = self.encode_u16(message.register)
        payload[32:34] = self.encode_u16(length)
        payload[34 : 34 + length] = message.data
        return bytes(payload)
