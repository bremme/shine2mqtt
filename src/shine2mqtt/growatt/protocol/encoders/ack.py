from shine2mqtt.growatt.protocol.constants import ACK, NACK
from shine2mqtt.growatt.protocol.encoders.encoder import PayloadEncoder
from shine2mqtt.growatt.protocol.messages.ack import GrowattAckMessage


class AckPayloadEncoder(PayloadEncoder[GrowattAckMessage]):
    def __init__(self):
        super().__init__(GrowattAckMessage)

    def encode(self, message: GrowattAckMessage) -> bytes:
        payload = ACK if message.ack is True else NACK
        return payload
