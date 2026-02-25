from shine2mqtt.protocol.frame.header.header import MBAPHeader
from shine2mqtt.protocol.messages.decoder.decoder import MessageDecoder
from shine2mqtt.protocol.messages.ping.message import GrowattPingMessage


class PingRequestDecoder(MessageDecoder[GrowattPingMessage]):
    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattPingMessage:
        variables = {
            "datalogger_serial": self.decode_str(payload, 0, 10),
        }

        return GrowattPingMessage(
            header=header,
            **variables,
        )
