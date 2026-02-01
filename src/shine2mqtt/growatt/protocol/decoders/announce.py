from dataclasses import dataclass

from shine2mqtt.growatt.protocol.decoders.base import MessageDecoder
from shine2mqtt.growatt.protocol.messages import GrowattAnnounceMessage
from shine2mqtt.growatt.protocol.messages.announce import SafetyFunction
from shine2mqtt.growatt.protocol.messages.base import MBAPHeader

POWER_FACTOR_MODES = {
    0: "Unity PF",
    1: "Default PF curve",
    2: "User PF curve",
    4: "Q under-excited",
    5: "Q over-excited",
    6: "Volt-VAR",
    7: "Direct Q control",
}

LCD_LANGUAGE_MAP = {
    0: "Italian",
    1: "English",
    2: "German",
    3: "Spanish",
    4: "French",
    5: "Chinese",
    6: "Polish",
    7: "Portuguese",
    8: "Hungarian",
}


@dataclass
class AnnounceRequestDecoder(MessageDecoder[GrowattAnnounceMessage]):
    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattAnnounceMessage:
        return GrowattAnnounceMessage(
            header=header,
            # Custom Announce block ####################################################
            # first 70 bytes
            datalogger_serial=self.read_str(payload, 0, 10),
            # 10-30 is \x00
            inverter_serial=self.read_str(payload, 30, 10),
            # 40-60 is \x00
            # Holding registers (read/write) ###########################################
            # See 4.1 Holding Registers in Protocol document v1.20(page 9)
            # Offset of 71 in the announce payload, every register is 2 bytes
            remote_on_off=self.read_bool(payload, 71),
            safety_function=self._decode_safety_function(payload, 73),
            power_factor_memory=self.read_bool(payload, 75),
            active_power_ac_max=self.read_u16(payload, 77),
            reactive_power_ac_max=self.read_u16(payload, 79),
            power_factor=self._read_u16_scaled(payload, 81, 0.0001),
            rated_power_ac=self._read_u32_scaled(payload, 83, 0.1),
            rated_voltage_dc=self._read_u16_scaled(payload, 87, 0.1),
            inverter_fw_version=self._decode_inverter_fw_version(payload, 89),
            inverter_control_fw_version=self._decode_inverter_control_fw_version(payload, 95),
            lcd_language=self._decode_lcd_language(payload, 101),
            #
            device_type=self.read_str(payload, 139, 16).rstrip("\x00"),
            #
            timestamp=self._read_datetime(payload, offset=161, fmt="H"),
            voltage_ac_low_limit=self._read_u16_scaled(payload, 175, 0.1),
            voltage_ac_high_limit=self._read_u16_scaled(payload, 177, 0.1),
            frequency_ac_low_limit=self._read_u16_scaled(payload, 179, 0.01),
            frequency_ac_high_limit=self._read_u16_scaled(payload, 181, 0.01),
            power_factor_control_mode=self._decode_power_factor_control_mode(payload, 249),
        )

    def _decode_safety_function(self, payload: bytes, offset: int) -> SafetyFunction:
        value = self.read_u16(payload, offset)
        return SafetyFunction(
            spi=self.read_bit(value, 0),
            auto_test_start=self.read_bit(value, 1),
            low_voltage_fault_ride_through=self.read_bit(value, 2),
            frequency_derating=self.read_bit(value, 3),
            soft_start=self.read_bit(value, 4),
            demand_response_management_system=self.read_bit(value, 5),
            power_voltage_control=self.read_bit(value, 6),
            high_voltage_fault_ride_through=self.read_bit(value, 7),
            rate_of_change_of_frequency_protection=self.read_bit(value, 8),
            frequency_derating_recovery=self.read_bit(value, 9),
        )

    def _decode_power_factor_control_mode(self, payload: bytes, offset: int) -> str:
        value = self.read_u16(payload, offset)

        return POWER_FACTOR_MODES.get(value, "Unknown")

    def _decode_inverter_fw_version(self, payload: bytes, offset: int) -> str:
        return self.read_str(payload, offset, 6).rstrip("\x00")

    def _decode_inverter_control_fw_version(self, payload: bytes, offset: int) -> str:
        high = self.read_str(payload, offset, 2)
        mid = self.read_str(payload, offset + 2, 2)
        low = self.read_u16(payload, offset + 4)
        return f"{high}{mid}.{low}"

    def _decode_lcd_language(self, payload: bytes, offset: int) -> str:
        lang_code = self.read_u16(payload, offset)

        return LCD_LANGUAGE_MAP.get(lang_code, "Unknown")
