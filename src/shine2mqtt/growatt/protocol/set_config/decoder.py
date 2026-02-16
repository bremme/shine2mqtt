from shine2mqtt.growatt.protocol.ack.decoder import (
    MessageDecoder,
)
from shine2mqtt.growatt.protocol.config import ConfigRegistry, RegisterNotFoundError
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

    def __init__(self, config_registry: ConfigRegistry | None = None):
        self.config_registry = config_registry if config_registry else ConfigRegistry()

    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattSetConfigRequestMessage:
        datalogger_serial = self.decode_str(payload, 0, 10)
        register = self.decode_u16(payload, 30)
        length = self.decode_u16(payload, 32)

        # Decode value based on register config
        try:
            info = self.config_registry.get_register_info(register)
            if info.fmt == "s":
                value = self.decode_str(payload, 34, length)
            elif info.fmt == "B":
                value = self.decode_u8(payload, 34)
            elif info.fmt == "H":
                value = self.decode_u16(payload, 34)
            else:
                value = self.decode_str(payload, 34, length)
        except RegisterNotFoundError:
            # Unknown register, read as string
            value = self.decode_str(payload, 34, length)

        return GrowattSetConfigRequestMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register=register,
            length=length,
            value=value,
        )
