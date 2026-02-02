from shine2mqtt.growatt.protocol.constants import InverterStatus
from shine2mqtt.growatt.protocol.decoders.decoder import MessageDecoder
from shine2mqtt.growatt.protocol.messages.base import MBAPHeader
from shine2mqtt.growatt.protocol.messages.data import GrowattDataMessage


class DataRequestDecoder(MessageDecoder[GrowattDataMessage]):
    def decode(self, header: MBAPHeader, payload: bytes) -> GrowattDataMessage:
        return GrowattDataMessage(
            header=header,
            # Custom  data block #######################################################
            datalogger_serial=self.decode_str(payload, 0, 10),
            #
            # 10-30 is \x00
            #
            # Holding registers (read/write) ###########################################
            # See 4.1 Holding Registers in Protocol document v1.20(page 9)
            # 23 Serial NO
            inverter_serial=self.decode_str(payload, 30, 10),
            # 40-60 is \x00
            timestamp=self._decode_datetime(payload, offset=60, fmt="B"),
            # "year": struct.unpack_from(">B", data, 60)[0],              # 45  Sys Year  System time-year
            # "month": struct.unpack_from(">B", data, 61)[0],             # 46
            # "day": struct.unpack_from(">B", data, 62)[0],               # 47
            # "hour": struct.unpack_from(">B", data, 63)[0],              # 48
            # "min": struct.unpack_from(">B", data, 64)[0],               # 49
            # "sec": struct.unpack_from(">B", data, 65)[0],               # 50
            # "weekly": struct.unpack_from(">B", data, 66)[0],            # 51
            #
            # 67-70 is \x00
            #
            # Input registers (read) ###################################################
            # See 4.2 Input Reg -> Protocol document v1.20 (page 33)
            # See 4.2 Input Reg -> Protocol document v1.20 (page 48 for TL-X and TL-XH)
            # 0 Inverter Status
            inverter_status=InverterStatus(self.decode_u16(payload, 71)),
            # DC
            power_dc=self._decode_u32_scaled(payload, 73, 0.1),
            # DC 1
            voltage_dc_1=self._decode_u16_scaled(payload, 77, 0.1),
            current_dc_1=self._decode_u16_scaled(payload, 79, 0.1),
            power_dc_1=self._decode_u32_scaled(payload, 81, 0.1),
            # DC 2
            voltage_dc_2=self._decode_u16_scaled(payload, 85, 0.1),
            current_dc_2=self._decode_u16_scaled(payload, 87, 0.1),
            power_dc_2=self._decode_u32_scaled(payload, 89, 0.1),
            # AC
            power_ac=self._decode_u32_scaled(payload, 117, 0.1),
            frequency_ac=self._decode_u16_scaled(payload, 121, 0.01),
            # AC 1
            voltage_ac_1=self._decode_u16_scaled(payload, 123, 0.1),
            current_ac_1=self._decode_u16_scaled(payload, 125, 0.1),
            power_ac_1=self._decode_u32_scaled(payload, 127, 0.1),
            # AC line
            voltage_ac_l1_l2=self._decode_u16_scaled(payload, 147, 0.1),
            voltage_ac_l2_l3=self._decode_u16_scaled(payload, 149, 0.1),
            voltage_ac_l3_l1=self._decode_u16_scaled(payload, 151, 0.1),
            total_run_time=self._decode_total_run_time(payload, 165),
            # Energy AC
            energy_ac_today=self._decode_u32_scaled(payload, 169, 0.1),
            energy_ac_total=self._decode_u32_scaled(payload, 173, 0.1),
            # Energy DC
            energy_dc_total=self._decode_u32_scaled(payload, 177, 0.1),
            # Energy DC 1
            energy_dc_1_today=self._decode_u32_scaled(payload, 181, 0.1),
            energy_dc_1_total=self._decode_u32_scaled(payload, 185, 0.1),
            # Energy DC 2
            energy_dc_2_today=self._decode_u32_scaled(payload, 189, 0.1),
            energy_dc_2_total=self._decode_u32_scaled(payload, 193, 0.1),
            # Energy DC 3
            # energy_dc_3_today=self._read_u32_scaled(payload, 197, 0.1),
            # energy_dc_3_total=self._read_u32_scaled(payload, 201, 0.1),
            # Temperatures
            # FIXME
            # temperature=self._read_u16_scaled(payload, 257, 0.1),
            temperature=0.0,
            # temperature_ipm=self._read_u16_scaled(payload, 259, 0.1),
            # temperature_boost=self._read_u16_scaled(payload, 261, 0.1),
        )

    def _decode_total_run_time(self, payload: bytes, offset: int) -> int:
        raw_value_seconds = self.decode_u32(payload, offset)
        hours = int(raw_value_seconds / (60 * 60))
        return hours


class BufferDataRequestDecoder(DataRequestDecoder):
    pass
