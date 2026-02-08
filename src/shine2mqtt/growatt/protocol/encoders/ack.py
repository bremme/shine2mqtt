from shine2mqtt.growatt.protocol.constants import ACK, NACK
from shine2mqtt.growatt.protocol.encoders.encoder import PayloadEncoder
from shine2mqtt.growatt.protocol.messages.ack import GrowattAckMessage


class AckPayloadEncoder(PayloadEncoder[GrowattAckMessage]):
    ACK_MESSAGE_PAYLOAD_SIZE = 1

    def __init__(self):
        super().__init__(GrowattAckMessage)

    def encode(self, message: GrowattAckMessage) -> bytes:
        payload = bytearray(self.ACK_MESSAGE_PAYLOAD_SIZE)
        payload[0] = (ACK if message.ack is True else NACK)[0]
        return bytes(payload)
