from typing import override

from shine2mqtt.protocol.frame.header.header import MBAPHeader
from shine2mqtt.protocol.messages.constants import ACK
from shine2mqtt.protocol.messages.decoder.decoder import MessageDecoder
from shine2mqtt.protocol.messages.write_register.write_register import (
    GrowattWriteMultipleRegistersResponseMessage,
    GrowattWriteSingleRegisterResponseMessage,
)


class GrowattWriteSingleRegisterResponseDecoder(
    MessageDecoder[GrowattWriteSingleRegisterResponseMessage]
):
    @override
    def decode(
        self, header: MBAPHeader, payload: bytes
    ) -> GrowattWriteSingleRegisterResponseMessage:
        datalogger_serial = self.decode_str(payload, 0, 10)
        # 10-30 is \x00 (padding)
        register = self.decode_u16(payload, 30)
        ack = self.decode_u8(payload, 32) == ACK
        value = self.decode_u16(payload, 33)

        return GrowattWriteSingleRegisterResponseMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register=register,
            ack=ack,
            value=value,
        )


class GrowattWriteMultipleRegistersResponseDecoder(
    MessageDecoder[GrowattWriteMultipleRegistersResponseMessage]
):
    @override
    def decode(
        self, header: MBAPHeader, payload: bytes
    ) -> GrowattWriteMultipleRegistersResponseMessage:
        datalogger_serial = self.decode_str(payload, 0, 10)
        # 10-30 is \x00 (padding)
        register_start = self.decode_u16(payload, 30)
        register_end = self.decode_u16(payload, 32)
        ack = self.decode_u8(payload, 34) == ACK

        return GrowattWriteMultipleRegistersResponseMessage(
            header=header,
            datalogger_serial=datalogger_serial,
            register_start=register_start,
            register_end=register_end,
            ack=ack,
        )
