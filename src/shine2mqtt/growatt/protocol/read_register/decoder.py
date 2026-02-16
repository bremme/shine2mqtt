from shine2mqtt.growatt.protocol.base.decoder import MessageDecoder
from shine2mqtt.growatt.protocol.header.header import MBAPHeader
from shine2mqtt.growatt.protocol.read_register.read_register import (
    GrowattReadRegisterResponseMessage,
)


class ReadRegistersResponseDecoder(MessageDecoder[GrowattReadRegisterResponseMessage]):
    def __init__(self, register_registry=None):
        self.register_registry = register_registry

    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattReadRegisterResponseMessage:
        datalogger_serial = self.decode_str(payload, 0, 10)
        # padding
        register_start = self.decode_u16(payload, 30)
        register_end = self.decode_u16(payload, 32)

        num_data_bytes = (register_end - register_start + 1) * 2

        data = payload[34 : 34 + num_data_bytes].hex()
        data_u16 = {}

        # decode raw data
        for reg in range(register_start, register_end + 1):
            offset = 34 + (reg - register_start) * 2
            data_u16[reg] = self.decode_u16(payload, offset)

        return GrowattReadRegisterResponseMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register_start=register_start,
            register_end=register_end,
            data=data,
            data_u16=data_u16,
        )
