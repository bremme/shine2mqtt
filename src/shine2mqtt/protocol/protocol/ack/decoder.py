from shine2mqtt.protocol.protocol.ack.ack import GrowattAckMessage
from shine2mqtt.protocol.protocol.base.decoder import MessageDecoder
from shine2mqtt.protocol.protocol.base.message import MBAPHeader
from shine2mqtt.protocol.protocol.constants import ACK


class AckMessageResponseDecoder(MessageDecoder[GrowattAckMessage]):
    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattAckMessage:
        ack = payload == ACK
        return GrowattAckMessage(header=header, ack=ack)
