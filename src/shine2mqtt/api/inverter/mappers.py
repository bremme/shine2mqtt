from shine2mqtt.api.inverter.models import InverterRegister
from shine2mqtt.growatt.protocol.read_register.read_register import (
    GrowattReadRegisterResponseMessage,
)


def read_registers_response_to_inverter_registers(
    message: GrowattReadRegisterResponseMessage,
) -> list[InverterRegister]:
    inverter_registers = []
    for register, value in message.data_u16.items():
        inverter_registers.append(
            InverterRegister(
                address=register,
                value=value,
            )
        )
    return inverter_registers
