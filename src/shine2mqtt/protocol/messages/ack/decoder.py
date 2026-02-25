from shine2mqtt.protocol.frame.header.header import MBAPHeader
from shine2mqtt.protocol.messages.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.messages.constants import ACK
from shine2mqtt.protocol.messages.decoder.decoder import MessageDecoder


class AckMessageResponseDecoder(MessageDecoder[GrowattAckMessage]):
    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattAckMessage:
        ack = payload == ACK
        return GrowattAckMessage(header=header, ack=ack)
