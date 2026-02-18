from shine2mqtt.protocol.protocol.base.decoder import MessageDecoder
from shine2mqtt.protocol.protocol.base.message import MBAPHeader
from shine2mqtt.protocol.protocol.ping.message import GrowattPingMessage


class PingRequestDecoder(MessageDecoder[GrowattPingMessage]):
    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattPingMessage:
        variables = {
            "datalogger_serial": self.decode_str(payload, 0, 10),
        }

        return GrowattPingMessage(
            header=header,
            **variables,
        )
