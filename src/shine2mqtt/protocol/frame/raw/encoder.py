from shine2mqtt.protocol.frame.raw.raw import GrowattRawMessage
from shine2mqtt.protocol.messages.encoder.encoder import PayloadEncoder


class RawRequestPayloadEncoder(PayloadEncoder[GrowattRawMessage]):
    def __init__(self):
        super().__init__(GrowattRawMessage)

    def encode(self, message: GrowattRawMessage) -> bytes:
        return message.payload
