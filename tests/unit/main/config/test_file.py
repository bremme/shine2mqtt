from pathlib import Path
from tempfile import TemporaryDirectory

from shine2mqtt.main.config.file import ConfigFileLoader


class TestConfigFileLoader:
    def test_load_with_explicit_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("setting: enabled\n")

            loader = ConfigFileLoader(environ={}, default_path=Path("ignored.yaml"))
            result = loader.load(config_path)

            assert result == {"setting": "enabled"}

    def test_load_from_env_var_when_no_explicit_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("from: env\n")

            loader = ConfigFileLoader(
                environ={"SHINE2MQTT_CONFIG_FILE": str(config_path)},
                default_path=Path("ignored.yaml"),
            )
            result = loader.load()

            assert result == {"from": "env"}

    def test_load_from_default_path_when_available(self) -> None:
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("from: default\n")

            loader = ConfigFileLoader(environ={}, default_path=config_path)
            result = loader.load()

            assert result == {"from": "default"}

    def test_load_returns_empty_dict_when_no_config_found(self) -> None:
        loader = ConfigFileLoader(environ={}, default_path=Path("nonexistent.yaml"))

        result = loader.load()

        assert result == {}

    def test_precedence_explicit_over_env_over_default(self) -> None:
        with TemporaryDirectory() as tmpdir:
            explicit_path = Path(tmpdir) / "explicit.yaml"
            explicit_path.write_text("from: explicit\n")

            env_path = Path(tmpdir) / "env.yaml"
            env_path.write_text("from: env\n")

            default_path = Path(tmpdir) / "default.yaml"
            default_path.write_text("from: default\n")

            loader = ConfigFileLoader(
                environ={"SHINE2MQTT_CONFIG_FILE": str(env_path)},
                default_path=default_path,
            )

            result = loader.load(explicit_path)

            assert result == {"from": "explicit"}
