import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shine2mqtt import util
from shine2mqtt.api.config import ApiConfig
from shine2mqtt.growatt.client.config import SimulatedClientConfig
from shine2mqtt.growatt.server.config import GrowattServerConfig
from shine2mqtt.mqtt.config import MqttConfig

ENV_PREFIX = "SHINE2MQTT_"

NESTED_DELIMITER = "__"


class ApplicationConfig(BaseSettings):
    log_level: str = logging.getLevelName(logging.INFO)
    log_color: bool = True
    config_file: Path | None = None
    capture_data: bool = False
    mqtt: MqttConfig = Field(default_factory=MqttConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    server: GrowattServerConfig = Field(default_factory=GrowattServerConfig)
    simulated_client: SimulatedClientConfig = Field(default_factory=SimulatedClientConfig)

    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        env_nested_delimiter=NESTED_DELIMITER,
        env_file=".env",
    )

    @staticmethod
    def create(base: dict, override: dict) -> ApplicationConfig:
        merged_config = util.merge_dict(base=base, override=override)
        return ApplicationConfig(**merged_config)
