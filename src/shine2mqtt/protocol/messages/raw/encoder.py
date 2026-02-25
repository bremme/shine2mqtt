from shine2mqtt.protocol.messages.encoder.encoder import PayloadEncoder
from shine2mqtt.protocol.messages.raw.raw import GrowattRawMessage


class RawRequestPayloadEncoder(PayloadEncoder[GrowattRawMessage]):
    def __init__(self):
        super().__init__(GrowattRawMessage)

    def encode(self, message: GrowattRawMessage) -> bytes:
        return message.payload
