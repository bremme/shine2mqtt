from shine2mqtt.growatt.protocol.encoders.base import BaseEncoder
from shine2mqtt.growatt.protocol.messages.config import (
    GrowattGetConfigRequestMessage,
    GrowattGetConfigResponseMessage,
    GrowattSetConfigRequestMessage,
)


class SetConfigRequestPayloadEncoder(BaseEncoder[GrowattSetConfigRequestMessage]):
    def __init__(self):
        super().__init__(GrowattSetConfigRequestMessage)

    def encode(self, message: GrowattSetConfigRequestMessage) -> bytes:
        payload = self.encode_string(message.datalogger_serial, 10)
        payload += self.encode_uint16(message.register)
        payload += self.encode_uint16(message.length)
        if type(message.value) is int:
            payload += self.encode_uint16(message.value)
        elif type(message.value) is str:
            payload += self.encode_string(message.value, message.length)
        else:
            raise ValueError("Invalid type of value attribute")
        return payload


class GetConfigRequestPayloadEncoder(BaseEncoder[GrowattGetConfigRequestMessage]):
    def __init__(self):
        super().__init__(GrowattGetConfigRequestMessage)

    def encode(self, message: GrowattGetConfigRequestMessage) -> bytes:
        payload = self.encode_string(message.datalogger_serial, 10)
        payload += self.encode_uint16(message.register_start)
        payload += self.encode_uint16(message.register_end)
        return payload


class GetConfigResponsePayloadEncoder(BaseEncoder[GrowattGetConfigResponseMessage]):
    def __init__(self):
        super().__init__(GrowattGetConfigResponseMessage)

    def encode(self, message: GrowattGetConfigResponseMessage) -> bytes:
        size = 10 + 20 + 2 + 2 + len(message.data)
        payload = bytearray(size)
        payload[0:10] = self.encode_string(message.datalogger_serial, 10)
        # 10-30 is \x00 (padding)
        payload[30:32] = self.encode_uint16(message.register)
        payload[32:34] = self.encode_uint16(message.length)
        payload[34 : 34 + len(message.data)] = message.data
        return bytes(payload)
