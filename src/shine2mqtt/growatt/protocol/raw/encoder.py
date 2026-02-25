from shine2mqtt.growatt.protocol.base.encoder import PayloadEncoder
from shine2mqtt.growatt.protocol.raw.raw import GrowattRawMessage


class RawRequestPayloadEncoder(PayloadEncoder[GrowattRawMessage]):
    def __init__(self):
        super().__init__(GrowattRawMessage)

    def encode(self, message: GrowattRawMessage) -> bytes:
        return message.payload
