from typing import Any

from aiomqtt import Client, ProtocolVersion, Will

from shine2mqtt.adapters.mqtt.config import MqttServerConfig
from shine2mqtt.adapters.mqtt.message import MqttMessage
from shine2mqtt.util.logger import logger


class MqttClient:
    def __init__(self, config: MqttServerConfig, will_message: MqttMessage | None = None):
        will = (
            Will(
                topic=will_message.topic,
                payload=will_message.payload,
                qos=will_message.qos,
                retain=will_message.retain,
            )
            if will_message
            else None
        )

        self._mqtt_config: dict[str, Any] = {
            "hostname": config.host,
            "port": config.port,
            "username": config.username,
            "password": config.password,
            "identifier": config.client_id,
            "protocol": ProtocolVersion.V5,
            "logger": logger,
            "will": will,
        }

    def connect(self) -> Client:
        return Client(**self._mqtt_config)
