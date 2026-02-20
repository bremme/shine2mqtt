from dataclasses import dataclass
from enum import Enum


class FunctionCode(Enum):
    ANNOUNCE = 0x03  # 3 (holding registers)
    DATA = 0x04  # 4 (input registers)
    BUFFERED_DATA = 0x50  # 80 (input registers)
    PING = 0x16  # 22

    SET_CONFIG = 0x18  # 24
    GET_CONFIG = 0x19  # 25
    # REBOOT = 0x20 ?

    READ_REGISTERS = 0x05  # 5 (custom code, not standard Modbus)
    WRITE_SINGLE_HOLDING_REGISTER = 0x06
    WRITE_MULTIPLE_HOLDING_REGISTERS = 0x10

    # default Modbus function codes
    # https://en.wikipedia.org/wiki/Modbus#Public_function_codes
    X02_02 = 0x02  # Read Discrete Inputs
    X01_01 = 0x01  # Read Coils
    X05_05 = 0x05  # Write Single Coil
    X0F_15 = 0x0F  # Write Multiple Coils

    X03_03 = 0x03  # Read Multiple Holding Registers
    X06_06 = 0x06  # Write Single Holding Register
    X04_04 = 0x04  # Read Input Registers
    X10_16 = 0x10  # Write Multiple Holding Registers
    X14_20 = 0x14  # (20) Read File Record
    X15_21 = 0x15  # (21) Write File Record
    X16_22 = 0x16  # (22) Mask Write Register
    X17_23 = 0x17  # (23) Read/Write Multiple Registers
    X18_24 = 0x18  # (24) Read FIFO Queue

    X19_25 = 0x19  # (25) Get Config
    X20_32 = 0x20  # (32) Reboot
    X32_50 = 0x32  # (50)
    X50_80 = 0x50  # (80)


@dataclass
class MBAPHeader:
    transaction_id: int
    protocol_id: int
    length: int
    unit_id: int
    # TODO: strictly speaking, function code is not part of the MBAP header
    # [MBAP Header][Function Code][Data]
    # Function Code and Data are part of the PDU (Protocol Data Unit)
    function_code: FunctionCode

    def asdict(self) -> dict:
        """Serialize header to dict with function_code as hex value"""
        return {
            "transaction_id": self.transaction_id,
            "protocol_id": self.protocol_id,
            "length": self.length,
            "unit_id": self.unit_id,
            "function_code": self.function_code.value,
        }

    @classmethod
    def fromdict(cls, data: dict) -> MBAPHeader:
        """Deserialize header from dict with function_code as hex value"""
        return cls(
            transaction_id=data["transaction_id"],
            protocol_id=data["protocol_id"],
            length=data["length"],
            unit_id=data["unit_id"],
            function_code=FunctionCode(data["function_code"]),
        )
