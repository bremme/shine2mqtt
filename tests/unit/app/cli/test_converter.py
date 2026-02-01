from argparse import Namespace

from shine2mqtt.app.cli.converter import CliArgDictConverter


class TestCliArgDictConverter:
    def test_convert_removes_none_values(self) -> None:
        args = Namespace(
            log_level="INFO",
            api__enabled=None,
            mqtt__host="localhost",
            capture_data=None,
        )

        result = CliArgDictConverter.convert(args)

        assert result == {
            "log_level": "INFO",
            "mqtt": {"host": "localhost"},
        }

    def test_convert_creates_nested_dict_from_flat_keys(self) -> None:
        args = Namespace(
            mqtt__server__host="broker.local",
            mqtt__server__port=1883,
            api__port=8080,
            log_level="DEBUG",
        )

        result = CliArgDictConverter.convert(args)

        assert result == {
            "mqtt": {"server": {"host": "broker.local", "port": 1883}},
            "api": {"port": 8080},
            "log_level": "DEBUG",
        }

    def test_convert_with_mixed_types(self) -> None:
        args = Namespace(
            log_level="WARNING",
            mqtt__port=1883,
            api__enabled=True,
            capture_data=False,
        )

        result = CliArgDictConverter.convert(args)

        assert result == {
            "log_level": "WARNING",
            "mqtt": {"port": 1883},
            "api": {"enabled": True},
            "capture_data": False,
        }

    def test_convert_with_empty_namespace(self) -> None:
        args = Namespace()

        result = CliArgDictConverter.convert(args)

        assert result == {}

    def test_convert_with_only_none_values(self) -> None:
        args = Namespace(
            api__enabled=None,
            capture_data=None,
            log_level=None,
        )

        result = CliArgDictConverter.convert(args)

        assert result == {}
