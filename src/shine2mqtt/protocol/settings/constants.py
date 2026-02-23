# register constants
UPDATE_INTERVAL_REGISTER = 4
DATALOGGER_IP_ADDRESS_REGISTER = 14
DATALOGGER_MAC_ADDRESS_REGISTER = 16
DATALOGGER_SERVER_IP_ADDRESS_REGISTER = 17
DATALOGGER_SW_VERSION_REGISTER = 21
DATALOGGER_SYSTEM_TIME_REGISTER = 31
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
    15: {"name": "port", "description": "Local Port", "fmt": "s"},
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
    18: {"name": "server_port", "description": "Server Port", "fmt": "s"},
    19: {"name": "server", "description": "Server", "fmt": "s"},
    20: {"name": "device_type", "description": "Device Type", "fmt": "s"},
    DATALOGGER_SW_VERSION_REGISTER: {
        "name": "datalogger_sw_version",
        "description": "Datalogger software Version",
        "fmt": "s",
    },
    22: {
        "name": "datalogger_hw_version",
        "description": "Datalogger Hardware Version",
        "fmt": "s",
    },
    25: {"name": "netmask", "description": "Netmask", "fmt": "s"},
    26: {"name": "gateway_ip_address", "description": "Gateway IP", "fmt": "s"},
    # 27-30 are unknown
    31: {"name": "date", "description": "Date", "fmt": "s"},
    32: {"name": "reboot", "description": "Reboot", "fmt": "s"},
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
    DATALOGGER_SYSTEM_TIME_REGISTER: {
        "name": "system_time",
        "description": "System time",
        "fmt": "s",
    },
}

ANNOUNCE_REGISTER = {}
DATA_REGISTER = {}
