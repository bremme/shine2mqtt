import struct

from shine2mqtt.growatt.protocol.decoders.announce import LCD_LANGUAGE_MAP, POWER_FACTOR_MODES
from shine2mqtt.growatt.protocol.encoders.encoder import PayloadEncoder
from shine2mqtt.growatt.protocol.messages.announce import GrowattAnnounceMessage, SafetyFunction

ANNOUNCE_MESSAGE_PAYLOAD_SIZE = 575


class AnnouncePayloadEncoder(PayloadEncoder[GrowattAnnounceMessage]):
    def __init__(self):
        super().__init__(GrowattAnnounceMessage)

    def encode(self, message: GrowattAnnounceMessage) -> bytes:
        payload = bytearray(ANNOUNCE_MESSAGE_PAYLOAD_SIZE)

        # Custom Announce block ########################################################
        # first 70 bytes
        # Datalogger serial (0-10)
        payload[0:10] = self.encode_str(message.datalogger_serial, 10)
        # 10-30 is \x00 (padding)
        payload[30:40] = self.encode_str(message.inverter_serial, 10)
        # 40-60 is \x00 (padding)
        # 60-70 is unknown
        # Holding registers (read/write) ###############################################
        # See 4.1 Holding Registers in Protocol document v1.20(page 9)
        # Offset of 71 in the announce payload, every register is 2 bytes
        payload[71:73] = self.encode_bool(message.remote_on_off)
        payload[73:75] = self.encode_safety_function(message.safety_function)
        payload[75:77] = self.encode_bool(message.power_factor_memory)
        payload[77:79] = self.encode_u16(message.active_power_ac_max)
        payload[79:81] = self.encode_u16(message.reactive_power_ac_max)
        payload[81:83] = self.encode_u16(int(message.power_factor / 0.0001))
        payload[83:87] = self.encode_u32(int(message.rated_power_ac / 0.1))
        payload[87:89] = self.encode_u16(int(message.rated_voltage_dc / 0.1))

        payload[89:95] = self.encode_str(message.inverter_fw_version, 6)

        payload[95:101] = self.encode_inverter_control_fw_version(
            message.inverter_control_fw_version
        )

        # LCD language (101-103)
        payload[101:103] = self.encode_lcd_language(message.lcd_language)

        # Device type (139-155)
        payload[139:155] = self.encode_str(message.device_type, 16)

        # System datetime (161-175)
        payload[161:163] = struct.pack(">H", message.timestamp.year)
        payload[163:165] = struct.pack(">H", message.timestamp.month)
        payload[165:167] = struct.pack(">H", message.timestamp.day)
        payload[167:169] = struct.pack(">H", message.timestamp.hour)
        payload[169:171] = struct.pack(">H", message.timestamp.minute)
        payload[171:173] = struct.pack(">H", message.timestamp.second)
        payload[173:175] = struct.pack(">H", message.timestamp.weekday())

        # Voltage and frequency limits
        payload[175:177] = self.encode_u16(int(message.voltage_ac_low_limit * 10))
        payload[177:179] = self.encode_u16(int(message.voltage_ac_high_limit * 10))
        payload[179:181] = self.encode_u16(int(message.frequency_ac_low_limit * 100))
        payload[181:183] = self.encode_u16(int(message.frequency_ac_high_limit * 100))

        # Power factor control mode (249-251)
        payload[249:251] = self.encode_power_factor_control_mode(message.power_factor_control_mode)

        return bytes(payload)

    def encode_inverter_control_fw_version(self, version: str) -> bytes:
        # Format: "ZAAA.8" -> high=ZA, mid=AA, low=8

        version_parts = version.split(".")
        if len(version_parts) != 2:
            raise ValueError(f"Invalid inverter control firmware version format: {version}")

        high = version_parts[0][:2]
        mid = version_parts[0][2:4]
        low = int(version_parts[1])

        encoded = bytearray(6)
        encoded[0:2] = self.encode_str(high, 2)
        encoded[2:4] = self.encode_str(mid, 2)
        encoded[4:6] = self.encode_u16(low)

        return bytes(encoded)

    def encode_lcd_language(self, language: str) -> bytes:
        languages = list(LCD_LANGUAGE_MAP.values())

        try:
            language_code = languages.index(language)
        except ValueError as e:
            raise ValueError(f"Unknown LCD language: {language}") from e

        return self.encode_u16(language_code)

    def encode_safety_function(self, safety_function: SafetyFunction) -> bytes:
        value = 0

        value |= self.set_bit(value, 0, safety_function.spi)
        value |= self.set_bit(value, 1, safety_function.auto_test_start)
        value |= self.set_bit(value, 2, safety_function.low_voltage_fault_ride_through)
        value |= self.set_bit(value, 3, safety_function.frequency_derating)
        value |= self.set_bit(value, 4, safety_function.soft_start)
        value |= self.set_bit(value, 5, safety_function.demand_response_management_system)
        value |= self.set_bit(value, 6, safety_function.power_voltage_control)
        value |= self.set_bit(value, 7, safety_function.high_voltage_fault_ride_through)
        value |= self.set_bit(value, 8, safety_function.rate_of_change_of_frequency_protection)
        value |= self.set_bit(value, 9, safety_function.frequency_derating_recovery)

        return self.encode_u16(value)

    def encode_power_factor_control_mode(self, mode: str) -> bytes:
        modes = list(POWER_FACTOR_MODES.values())
        try:
            power_factor_index = modes.index(mode)
        except ValueError as e:
            raise ValueError(f"Unknown power factor control mode: {mode}") from e

        return self.encode_u16(power_factor_index)
