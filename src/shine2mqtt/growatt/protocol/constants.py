from enum import Enum

ACK = b"\x00"
NACK = b"\x03"

ENCRYPTION_KEY = b"Growatt"
DECRYPTION_KEY = ENCRYPTION_KEY

# Modbus function codes
# https://en.wikipedia.org/wiki/Modbus#Public_function_codes
READ_INPUT_REGISTERS = 4
READ_MULTIPLE_HOLDING_REGISTERS = 3
WRITE_SINGLE_HOLDING_REGISTER = 6
WRITE_MULTIPLE_HOLDING_REGISTERS = 16


class FunctionCode(Enum):
    ANNOUNCE = 0x03  # 3 (READ_MULTIPLE_HOLDING_REGISTERS)
    DATA = 0x04  # 4 (READ_INPUT_REGISTERS)
    PING = 0x16  # 22
    SET_CONFIG = 0x18  # 24
    GET_CONFIG = 0x19  # 25
    BUFFERED_DATA = 0x50  # 80
    # REBOOT = 0x20 ?

    READ_REGISTERS = 0x05  # 5 (custom code, not standard Modbus)
    WRITE_SINGLE_HOLDING_REGISTER = 0x06
    WRITE_MULTIPLE_HOLDING_REGISTERS = 0x10

    # default Modbus function codes
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


class InverterStatus(Enum):
    WAITING = 0
    NORMAL = 1
    FAULT = 3


UPDATE_INTERVAL_REGISTER = 4
DATALOGGER_IP_ADDRESS_REGISTER = 14
DATALOGGER_MAC_ADDRESS_REGISTER = 16
DATALOGGER_SERVER_IP_ADDRESS_REGISTER = 17
DATALOGGER_SW_VERSION_REGISTER = 21
DATALOGGER_WIFI_SSID_REGISTER = 56
DATALOGGER_WIFI_PASSWORD_REGISTER = 57

CONFIG_REGISTERS = {
    4: {
        "name": "update_interval",
        "description": "Update Interval min",
        "fmt": "s",
    },
    5: {
        "name": "modbus_range_low",
        "description": "Modbus Range low",
        "fmt": "s",
    },
    6: {
        "name": "modbus_range_high",
        "description": "Modbus Range high",
        "fmt": "s",
    },
    # 7 is unknown
    8: {
        "name": "datalogger_serial",
        "description": "Datalogger Serial Number",
        "fmt": "s",
    },
    # 9-13 are unknown
    DATALOGGER_IP_ADDRESS_REGISTER: {
        "name": "ip_address",
        "description": "Local IP",
        "fmt": "s",
    },  # 0x0E
    15: {"name": "port", "description": "Local Port", "fmt": "s"},  # 0x0F
    DATALOGGER_MAC_ADDRESS_REGISTER: {
        "name": "mac_address",
        "description": "Mac Address",
        "fmt": "s",
    },  # 0x10
    DATALOGGER_SERVER_IP_ADDRESS_REGISTER: {
        "name": "server_ip_address",
        "description": "Server IP",
        "fmt": "s",
    },  # 0x11
    18: {"name": "server_port", "description": "Server Port", "fmt": "s"},  # 0x12
    19: {"name": "server", "description": "Server", "fmt": "s"},  # 0x13
    20: {"name": "device_type", "description": "Device Type", "fmt": "s"},  # 0x14
    DATALOGGER_SW_VERSION_REGISTER: {
        "name": "datalogger_sw_version",
        "description": "Datalogger software Version",  # 0x15
        "fmt": "s",
    },
    22: {
        "name": "datalogger_hw_version",
        "description": "Datalogger Hardware Version",  # 0x16
        "fmt": "s",
    },
    25: {"name": "netmask", "description": "Netmask", "fmt": "s"},  # 0x19
    26: {"name": "gateway_ip_address", "description": "Gateway IP", "fmt": "s"},  # 0x1A
    # 27-30 are unknown
    31: {"name": "date", "description": "Date", "fmt": "s"},  # 0x1F
    32: {"name": "reboot", "description": "Reboot", "fmt": "s"},  # ?,  # ??? # 0x20
    DATALOGGER_WIFI_SSID_REGISTER: {
        "name": "wifi_ssid",
        "description": "WiFi SSID",
        "fmt": "s",
    },  # 0x38
    DATALOGGER_WIFI_PASSWORD_REGISTER: {
        "name": "wifi_password",
        "description": "WiFi password",
        "fmt": "s",
    },
}

ANNOUNCE_REGISTER = {}
DATA_REGISTER = {}
