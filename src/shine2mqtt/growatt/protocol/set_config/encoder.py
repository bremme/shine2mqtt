from shine2mqtt.growatt.protocol.base.encoder import PayloadEncoder
from shine2mqtt.growatt.protocol.set_config.set_config import GrowattSetConfigRequestMessage


class SetConfigRequestPayloadEncoder(PayloadEncoder[GrowattSetConfigRequestMessage]):
    def __init__(self):
        super().__init__(GrowattSetConfigRequestMessage)

    def encode(self, message: GrowattSetConfigRequestMessage) -> bytes:
        length_value = len(message.value)
        size = 10 + 20 + 2 + 2 + length_value
        payload = bytearray(size)
        payload[0:10] = self.encode_str(message.datalogger_serial, 10)
        # 10-30 is \x00 (padding)
        payload[30:32] = self.encode_u16(message.register)
        payload[32:34] = self.encode_u16(length_value)
        payload[34 : 34 + length_value] = self.encode_str(message.value, length_value)
        return bytes(payload)
