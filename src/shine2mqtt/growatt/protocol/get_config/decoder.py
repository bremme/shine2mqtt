import struct

from loguru import logger

from shine2mqtt.growatt.protocol.ack.decoder import MessageDecoder
from shine2mqtt.growatt.protocol.config import ConfigRegistry, RegisterNotFoundError
from shine2mqtt.growatt.protocol.get_config.get_config import (
    GrowattGetConfigRequestMessage,
    GrowattGetConfigResponseMessage,
)
from shine2mqtt.growatt.protocol.header.header import MBAPHeader


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

    def __init__(self, config_registry: ConfigRegistry | None = None):
        self.config_registry = config_registry if config_registry else ConfigRegistry()

    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattGetConfigResponseMessage:
        datalogger_serial = self.decode_str(payload, 0, 10)
        # padding
        register = self.decode_u16(payload, 30)
        length = self.decode_u16(payload, 32)

        try:
            data = payload[34 : 34 + length]
        except struct.error:
            logger.error(
                f"Could not unpack get config response data for register {register} with length {length} and data length {len(data)}"
            )
            data = b""

        try:
            config = self.config_registry.get_register_info(register)
            value = self.decode_str(payload, 34, length)

            return GrowattGetConfigResponseMessage(
                header=header,
                datalogger_serial=datalogger_serial,
                register=register,
                data=data,
                name=config.name,
                description=config.description,
                value=value,
            )
        except RegisterNotFoundError:
            # Unknown register, return minimal response
            return GrowattGetConfigResponseMessage(
                header=header,
                datalogger_serial=datalogger_serial,
                register=register,
                data=data,
            )
