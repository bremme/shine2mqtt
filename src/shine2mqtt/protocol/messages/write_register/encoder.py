from shine2mqtt.protocol.messages.encoder.encoder import PayloadEncoder
from shine2mqtt.protocol.messages.write_register.write_register import (
    GrowattWriteMultipleRegistersRequestMessage,
    GrowattWriteSingleRegisterRequestMessage,
)


class GrowattWriteSingleRegisterPayloadEncoder(
    PayloadEncoder[GrowattWriteSingleRegisterRequestMessage]
):
    def __init__(self):
        super().__init__(GrowattWriteSingleRegisterRequestMessage)

    def encode(self, message: GrowattWriteSingleRegisterRequestMessage) -> bytes:
        size = 10 + 20 + 2 + 2
        payload = bytearray(size)
        payload[0:10] = self.encode_str(message.datalogger_serial, 10)
        # 10-30 is \x00 (padding)
        payload[30:32] = self.encode_u16(message.register)
        payload[32:34] = self.encode_u16(message.value)
        return bytes(payload)


class GrowattWriteMultipleRegistersPayloadEncoder(
    PayloadEncoder[GrowattWriteMultipleRegistersRequestMessage]
):
    def __init__(self):
        super().__init__(GrowattWriteMultipleRegistersRequestMessage)

    def encode(self, message: GrowattWriteMultipleRegistersRequestMessage) -> bytes:
        length_values = len(message.values)
        size = 10 + 20 + 2 + length_values
        payload = bytearray(size)
        payload[0:10] = self.encode_str(message.datalogger_serial, 10)
        # 10-30 is \x00 (padding)
        payload[30:32] = self.encode_u16(message.register_start)
        payload[32:34] = self.encode_u16(message.register_end)
        payload[34 : 34 + length_values] = message.values
        return bytes(payload)
