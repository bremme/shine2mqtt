from shine2mqtt.domain.events.base import DataloggerAnnouncedEvent, InverterStateUpdatedEvent
from shine2mqtt.domain.models.inverter import (
    InverterSettings,
    InverterState,
    InverterStatus,
    SafetyFunction,
)
from shine2mqtt.protocol.messages.announce.announce import GrowattAnnounceMessage


class MessageEventMapper:
    def map_announce_message_to_announce_event(
        self, message: GrowattAnnounceMessage
    ) -> DataloggerAnnouncedEvent:
        inverter_settings = InverterSettings(
            remote_on_off=message.remote_on_off,
            safety_function=SafetyFunction(**vars(message.safety_function)),
            power_factor_memory=message.power_factor_memory,
            active_power_ac_max=message.active_power_ac_max,
            reactive_power_ac_max=message.reactive_power_ac_max,
            power_factor=message.power_factor,
            rated_power_ac=message.rated_power_ac,
            rated_voltage_dc=message.rated_voltage_dc,
            inverter_fw_version=message.inverter_fw_version,
            inverter_control_fw_version=message.inverter_control_fw_version,
            lcd_language=message.lcd_language,
            device_type=message.device_type,
            timestamp=message.timestamp,
            voltage_ac_low_limit=message.voltage_ac_low_limit,
            voltage_ac_high_limit=message.voltage_ac_high_limit,
            frequency_ac_low_limit=message.frequency_ac_low_limit,
            frequency_ac_high_limit=message.frequency_ac_high_limit,
            power_factor_control_mode=message.power_factor_control_mode,
        )

        return DataloggerAnnouncedEvent(
            datalogger_serial=message.datalogger_serial,
            inverter_serial=message.inverter_serial,
            inverter_settings=inverter_settings,
            timestamp=message.timestamp,
        )

    def map_data_message_to_inverter_state_updated_event(
        self, message
    ) -> InverterStateUpdatedEvent:
        status = InverterStatus(message.inverter_status)

        state = InverterState(
            inverter_status=status,
            # DC
            power_dc=message.power_dc,
            # DC 1
            voltage_dc_1=message.voltage_dc_1,
            current_dc_1=message.current_dc_1,
            power_dc_1=message.power_dc_1,
            # DC 2
            voltage_dc_2=message.voltage_dc_2,
            current_dc_2=message.current_dc_2,
            power_dc_2=message.power_dc_2,
            # AC
            power_ac=message.power_ac,
            frequency_ac=message.frequency_ac,
            # AC 1
            voltage_ac_1=message.voltage_ac_1,
            current_ac_1=message.current_ac_1,
            power_ac_1=message.power_ac_1,
            # AC line
            voltage_ac_l1_l2=message.voltage_ac_l1_l2,
            voltage_ac_l2_l3=message.voltage_ac_l2_l3,
            voltage_ac_l3_l1=message.voltage_ac_l3_l1,
            #
            total_run_time=message.total_run_time,
            # Energy AC
            energy_ac_today=message.energy_ac_today,
            energy_ac_total=message.energy_ac_total,
            # Energy DC 1
            energy_dc_1_today=message.energy_dc_1_today,
            energy_dc_1_total=message.energy_dc_1_total,
            # Energy DC 2
            energy_dc_2_today=message.energy_dc_2_today,
            energy_dc_2_total=message.energy_dc_2_total,
            # Energy DC
            energy_dc_total=message.energy_dc_total,
            # Temperatures
            temperature=message.temperature,
        )

        return InverterStateUpdatedEvent(
            datalogger_serial=message.datalogger_serial,
            state=state,
            timestamp=message.timestamp,
        )
