from shine2mqtt.growatt.protocol.base.encoder import PayloadEncoder
from shine2mqtt.growatt.protocol.set_config.set_config import GrowattSetConfigRequestMessage


class SetConfigRequestPayloadEncoder(PayloadEncoder[GrowattSetConfigRequestMessage]):
    def __init__(self):
        super().__init__(GrowattSetConfigRequestMessage)

    def encode(self, message: GrowattSetConfigRequestMessage) -> bytes:
        if type(message.value) is int:
            value_bytes = self.encode_u16(message.value)
        elif type(message.value) is str:
            value_bytes = self.encode_str(message.value, message.length)
        else:
            raise ValueError("Invalid type of value attribute")

        size = 10 + 20 + 2 + 2 + len(value_bytes)
        payload = bytearray(size)
        payload[0:10] = self.encode_str(message.datalogger_serial, 10)
        # 10-30 is \x00 (padding)
        payload[30:32] = self.encode_u16(message.register)
        payload[32:34] = self.encode_u16(message.length)
        payload[34 : 34 + len(value_bytes)] = value_bytes
        return bytes(payload)
