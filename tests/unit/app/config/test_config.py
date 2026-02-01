import logging

from shine2mqtt.app.config.config import ApplicationConfig


class TestApplicationConfig:
    def test_create_with_empty_dicts(self) -> None:
        config = ApplicationConfig.create(base={}, override={})

        assert config.log_level == logging.getLevelName(logging.INFO)
        assert config.log_color is True
        assert config.config_file is None
        assert config.capture_data is False

    def test_create_with_base_config(self) -> None:
        base = {
            "log_level": "DEBUG",
            "capture_data": True,
            "mqtt": {"server": {"host": "broker.example.com"}},
        }

        config = ApplicationConfig.create(base=base, override={})

        assert config.log_level == "DEBUG"
        assert config.capture_data is True
        assert config.mqtt.server.host == "broker.example.com"

    def test_create_with_override_config(self) -> None:
        base = {
            "log_level": "DEBUG",
            "log_color": False,
            "config_file": "/etc/config.yaml",
            "capture_data": True,
            "mqtt": {"server": {"host": "broker.local", "port": 1883}},
            "api": {"enabled": True, "port": 8080},
            "simulated_client": {"enabled": True},
        }
        override = {"log_level": "WARNING", "mqtt": {"server": {"port": 8883}}}

        config = ApplicationConfig.create(base=base, override=override)

        assert config.log_level == "WARNING"
        assert config.mqtt.server.host == "broker.local"
        assert config.mqtt.server.port == 8883
