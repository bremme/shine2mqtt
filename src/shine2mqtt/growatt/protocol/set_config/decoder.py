from shine2mqtt.growatt.protocol.ack.decoder import (
    MessageDecoder,
)
from shine2mqtt.growatt.protocol.constants import ACK
from shine2mqtt.growatt.protocol.header.header import MBAPHeader
from shine2mqtt.growatt.protocol.set_config.set_config import (
    GrowattSetConfigRequestMessage,
    GrowattSetConfigResponseMessage,
)


class SetConfigResponseDecoder(MessageDecoder[GrowattSetConfigResponseMessage]):
    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattSetConfigResponseMessage:
        ack = payload == ACK
        return GrowattSetConfigResponseMessage(header=header, ack=ack)


class SetConfigRequestDecoder(MessageDecoder[GrowattSetConfigRequestMessage]):
    """Decoder for SET_CONFIG requests (server → client)"""

    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattSetConfigRequestMessage:
        datalogger_serial = self.decode_str(payload, 0, 10)
        register = self.decode_u16(payload, 30)
        length = self.decode_u16(payload, 32)

        value = self.decode_str(payload, 34, length)

        return GrowattSetConfigRequestMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register=register,
            value=value,
        )
