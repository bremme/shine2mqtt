from shine2mqtt.growatt.protocol.encoders.encoder import PayloadEncoder
from shine2mqtt.growatt.protocol.messages.config import GrowattSetConfigRequestMessage


class SetConfigRequestPayloadEncoder(PayloadEncoder[GrowattSetConfigRequestMessage]):
    def __init__(self):
        super().__init__(GrowattSetConfigRequestMessage)

    def encode(self, message: GrowattSetConfigRequestMessage) -> bytes:
        payload = self.encode_str(message.datalogger_serial, 10)
        payload += self.encode_u16(message.register)
        payload += self.encode_u16(message.length)
        if type(message.value) is int:
            payload += self.encode_u16(message.value)
        elif type(message.value) is str:
            payload += self.encode_str(message.value, message.length)
        else:
            raise ValueError("Invalid type of value attribute")
        return payload
