from datetime import datetime

from shine2mqtt.domain.events.events import DataloggerAnnouncedEvent, InverterStateUpdatedEvent
from shine2mqtt.domain.models.inverter import (
    InverterState,
    InverterStatus,
)
from shine2mqtt.protocol.messages.data.data import GrowattBufferedDataMessage, GrowattDataMessage
from shine2mqtt.protocol.session.state import ServerProtocolSessionState


class MessageEventMapper:
    def map_state_to_announce_event(
        self, state: ServerProtocolSessionState
    ) -> DataloggerAnnouncedEvent:
        return DataloggerAnnouncedEvent(
            datalogger_serial=state.datalogger.serial,
            timestamp=datetime.now(),
            datalogger=state.datalogger,
            inverter=state.inverter,
        )

    def map_data_message_to_inverter_state_updated_event(
        self, message: GrowattDataMessage | GrowattBufferedDataMessage
    ) -> InverterStateUpdatedEvent:
        status = InverterStatus(message.inverter_status.value)

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
