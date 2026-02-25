import json
from dataclasses import asdict
from typing import Any

from shine2mqtt.adapters.hass.map import (
    DATALOGGER_SENSOR_MAP,
    INVERTER_SENSOR_MAP,
)
from shine2mqtt.adapters.mqtt.config import MqttConfig
from shine2mqtt.adapters.mqtt.message import MqttMessage
from shine2mqtt.domain.events.events import DataloggerAnnouncedEvent, InverterStateUpdatedEvent
from shine2mqtt.domain.models.inverter import Inverter
from shine2mqtt.util.logger import logger


class MqttEventMapper:
    def __init__(self, config: MqttConfig):
        self._base_topic = config.base_topic
        self._availability_topic = config.availability_topic

    def map_availability(self, online: bool) -> MqttMessage:
        return MqttMessage(
            topic=self._availability_topic,
            payload="online" if online else "offline",
            qos=1,
            retain=True,
        )

    def map_inverter_state(self, event: InverterStateUpdatedEvent) -> list[MqttMessage]:
        return self._build_mqtt_messages(asdict(event.state), INVERTER_SENSOR_MAP, "inverter")

    def map_datalogger_announced(self, event: DataloggerAnnouncedEvent) -> list[MqttMessage]:
        inverter_fields = self._flatten_inverter_announce_fields(event.inverter)
        datalogger_fields = asdict(event.datalogger)
        return [
            *self._build_mqtt_messages(
                datalogger_fields, DATALOGGER_SENSOR_MAP, "datalogger", qos=1, retain=True
            ),
            *self._build_mqtt_messages(
                inverter_fields, INVERTER_SENSOR_MAP, "inverter", qos=1, retain=True
            ),
        ]

    def _flatten_inverter_announce_fields(self, inverter: Inverter) -> dict:
        return {
            "inverter_serial": inverter.serial,
            "inverter_fw_version": inverter.fw_version,
            "inverter_control_fw_version": inverter.control_fw_version,
            **asdict(inverter.settings),
        }

    def _build_mqtt_messages(
        self,
        fields: dict[str, Any],
        sensor_map: dict[str, dict[str, str]],
        device: str,
        qos: int = 0,
        retain: bool = False,
    ) -> list[MqttMessage]:
        messages = []
        for field, value in fields.items():
            if field not in sensor_map:
                logger.warning(f"No sensor mapping for '{field}', skipping MQTT publish")
                continue
            sensor = sensor_map[field]
            topic = f"{self._base_topic}/{device}/sensor/{sensor['entity_id']}"
            payload = json.dumps({"value": value})
            messages.append(MqttMessage(topic=topic, payload=payload, qos=qos, retain=retain))
        return messages
