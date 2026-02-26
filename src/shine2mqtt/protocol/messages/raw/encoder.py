from shine2mqtt.protocol.messages.encoder.encoder import PayloadEncoder
from shine2mqtt.protocol.messages.raw.raw import GrowattRawRequestMessage


class RawRequestPayloadEncoder(PayloadEncoder[GrowattRawRequestMessage]):
    def __init__(self):
        super().__init__(GrowattRawRequestMessage)

    def encode(self, message: GrowattRawRequestMessage) -> bytes:
        return message.payload
