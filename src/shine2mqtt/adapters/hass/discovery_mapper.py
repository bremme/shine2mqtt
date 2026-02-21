import json

from shine2mqtt.adapters.hass.discovery import HassDiscoveryPayloadBuilder
from shine2mqtt.adapters.mqtt.message import MqttMessage
from shine2mqtt.domain.events.events import DataloggerAnnouncedEvent
from shine2mqtt.util.logger import logger


class HassDiscoveryMapper:
    def __init__(self, discovery: HassDiscoveryPayloadBuilder, enabled: bool):
        self._payload_builder = discovery
        self._enabled = enabled
        self._announced: set[str] = set()

    def get_discovery_messages(self, event: DataloggerAnnouncedEvent) -> list[MqttMessage]:
        if not self._enabled or event.datalogger_serial in self._announced:
            return []

        logger.info(f"Building HASS discovery messages for datalogger '{event.datalogger_serial}'")
        self._announced.add(event.datalogger_serial)

        return [
            self._build_inverter_discovery(event),
            self._build_datalogger_discovery(event),
        ]

    def _build_inverter_discovery(self, event: DataloggerAnnouncedEvent) -> MqttMessage:
        payload = self._payload_builder.build_inverter_discovery_message(
            inverter_fw_version=event.inverter.fw_version,
            inverter_serial=event.inverter.serial,
        )
        return MqttMessage(
            topic=self._payload_builder.build_inverter_discovery_topic(),
            payload=json.dumps(payload),
            qos=1,
            retain=True,
        )

    def _build_datalogger_discovery(self, event: DataloggerAnnouncedEvent) -> MqttMessage:
        payload = self._payload_builder.build_datalogger_discovery_message(
            datalogger_sw_version=event.datalogger.sw_version,
            datalogger_serial=event.datalogger.serial,
        )
        return MqttMessage(
            topic=self._payload_builder.build_datalogger_discovery_topic(),
            payload=json.dumps(payload),
            qos=1,
            retain=True,
        )
