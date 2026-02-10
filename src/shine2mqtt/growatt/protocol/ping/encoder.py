from shine2mqtt.growatt.protocol.encoders import PayloadEncoder
from shine2mqtt.growatt.protocol.messages import GrowattPingMessage


class PingPayloadEncoder(PayloadEncoder[GrowattPingMessage]):
    def __init__(self):
        super().__init__(GrowattPingMessage)

    def encode(self, message: GrowattPingMessage) -> bytes:
        payload = bytearray(10)
        payload[0:10] = self.encode_str(message.datalogger_serial, 10)
        return bytes(payload)
