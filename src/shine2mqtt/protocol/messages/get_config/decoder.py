from shine2mqtt.protocol.frame.header.header import MBAPHeader
from shine2mqtt.protocol.messages.decoder.decoder import MessageDecoder
from shine2mqtt.protocol.messages.get_config.get_config import (
    GrowattGetConfigRequestMessage,
    GrowattGetConfigResponseMessage,
)
from shine2mqtt.protocol.settings.registry import RegisterNotFoundError, SettingsRegistry


class GetConfigRequestDecoder(MessageDecoder[GrowattGetConfigRequestMessage]):
    """Decoder for GET_CONFIG requests (server → client)"""

    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattGetConfigRequestMessage:
        datalogger_serial = self.decode_str(payload, 0, 10)
        register_start = self.decode_u16(payload, 10)
        register_end = self.decode_u16(payload, 12)

        return GrowattGetConfigRequestMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register_start=register_start,
            register_end=register_end,
        )


class GetConfigResponseDecoder(MessageDecoder[GrowattGetConfigResponseMessage]):
    """Decoder for GET_CONFIG responses (client → server)"""

    def __init__(self, config_registry: SettingsRegistry | None = None):
        self.config_registry = config_registry if config_registry else SettingsRegistry()

    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattGetConfigResponseMessage:
        datalogger_serial = self.decode_str(payload, 0, 10)
        # padding
        register = self.decode_u16(payload, 30)
        length = self.decode_u16(payload, 32)

        data = payload[34 : 34 + length]
        value = self.decode_str(payload, 34, length)

        try:
            register_info = self.config_registry.get_register_info(register)

            return GrowattGetConfigResponseMessage(
                header=header,
                datalogger_serial=datalogger_serial,
                register=register,
                data=data,
                value=value,
                name=register_info.name,
                description=register_info.description,
            )
        except RegisterNotFoundError:
            # Unknown register, return minimal response
            return GrowattGetConfigResponseMessage(
                header=header,
                datalogger_serial=datalogger_serial,
                register=register,
                data=data,
                value=value,
            )
