from shine2mqtt.growatt.protocol.messages import (
    GrowattSetConfigRequestMessage,
    MBAPHeader,
)

from shine2mqtt.growatt.protocol.ack.decoder import (
    AckMessageResponseDecoder,
    MessageDecoder,
)
from shine2mqtt.growatt.protocol.config import ConfigRegistry


class SetConfigResponseDecoder(AckMessageResponseDecoder):
    pass


class SetConfigRequestDecoder(MessageDecoder[GrowattSetConfigRequestMessage]):
    """Decoder for SET_CONFIG requests (server → client)"""

    def __init__(self, config_registry: ConfigRegistry | None = None):
        self.config_registry = config_registry if config_registry else ConfigRegistry()

    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattSetConfigRequestMessage:
        datalogger_serial = self.decode_str(payload, 0, 10)
        register = self.decode_u16(payload, 30)
        length = self.decode_u16(payload, 32)

        # Decode value based on register config
        config = self.config_registry.get_register_info(register)
        if config is None:
            # Unknown register, read as bytes
            value = self.decode_str(payload, 34, length)
        elif config.fmt == "s":
            value = self.decode_str(payload, 34, length)
        elif config.fmt == "B":
            value = self.decode_u8(payload, 34)
        elif config.fmt == "H":
            value = self.decode_u16(payload, 34)
        else:
            value = self.decode_str(payload, 34, length)

        return GrowattSetConfigRequestMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register=register,
            length=length,
            value=value,
        )
