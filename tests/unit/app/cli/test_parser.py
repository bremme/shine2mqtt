from pathlib import Path
from unittest.mock import patch

import pytest

from shine2mqtt.app.cli.parser import CliArgParser


class TestCliArgParser:
    def test_create_uses_sys_argv_and_package_name(self) -> None:
        with patch("sys.argv", ["shine2mqtt", "run"]):
            with patch("shine2mqtt.app.cli.parser.NAME", "shine2mqtt"):
                parser = CliArgParser.create()
                assert parser.prog == "shine2mqtt"
                assert parser.argv == ["run"]

    def test_run_subcommand_disables_simulated_client(self) -> None:
        args = CliArgParser(["run"], "app").parse()
        assert args.simulated_client__enabled is False

    def test_sim_subcommand_enables_simulated_client(self) -> None:
        args = CliArgParser(["sim"], "app").parse()
        assert args.simulated_client__enabled is True

    def test_run_with_full_mqtt_config(self) -> None:
        args = CliArgParser(
            [
                "--log-level",
                "DEBUG",
                "--log-color",
                "--config-file",
                "/path/to/config.yaml",
                "run",
                "--mqtt-host",
                "broker.local",
                "--mqtt-port",
                "1883",
                "--mqtt-username",
                "user",
                "--mqtt-password",
                "pass",
                "--mqtt-base-topic",
                "home/solar",
                "--mqtt-availability-topic",
                "home/status",
                "--mqtt-discovery",
                "--mqtt-discovery-inverter",
                "MIC 3000TL-X",
                "--mqtt-discovery-datalogger",
                "Shine Wifi-X",
            ],
            "app",
        ).parse()
        assert args.log_level == "DEBUG"
        assert args.log_color is True
        assert args.config_file == Path("/path/to/config.yaml")
        assert args.mqtt__server__host == "broker.local"
        assert args.mqtt__server__port == 1883
        assert args.mqtt__server__username == "user"
        assert args.mqtt__server__password == "pass"
        assert args.mqtt__base_topic == "home/solar"
        assert args.mqtt__availability_topic == "home/status"
        assert args.mqtt__discovery__enabled is True
        assert args.mqtt__discovery__inverter__model == "MIC 3000TL-X"
        assert args.mqtt__discovery__datalogger__model == "Shine Wifi-X"

    def test_run_with_server_and_api_config(self) -> None:
        args = CliArgParser(
            [
                "run",
                "--server-host",
                "0.0.0.0",
                "--server-port",
                "5279",
                "--api",
                "--api-host",
                "127.0.0.1",
                "--api-port",
                "8080",
                "--capture-data",
            ],
            "app",
        ).parse()
        assert args.server__host == "0.0.0.0"
        assert args.server__port == 5279
        assert args.api__enabled is True
        assert args.api__host == "127.0.0.1"
        assert args.api__port == 8080
        assert args.capture_data is True

    def test_run_defaults_for_optional_flags(self) -> None:
        args = CliArgParser(["run"], "app").parse()
        assert args.capture_data is None
        assert args.api__enabled is None
        assert args.mqtt__discovery__enabled is None

    def test_sim_with_server_config(self) -> None:
        args = CliArgParser(
            [
                "sim",
                "--server-host",
                "localhost",
                "--server-port",
                "5279",
            ],
            "app",
        ).parse()
        assert args.simulated_client__server_host == "localhost"
        assert args.simulated_client__server_port == 5279
        assert args.simulated_client__enabled is True

    def test_invalid_mqtt_port_type(self) -> None:
        with pytest.raises(SystemExit):
            CliArgParser(["run", "--mqtt-port", "not_a_number"], "app").parse()

    def test_invalid_server_port_type(self) -> None:
        with pytest.raises(SystemExit):
            CliArgParser(["run", "--server-port", "not_a_number"], "app").parse()

    def test_invalid_api_port_type(self) -> None:
        with pytest.raises(SystemExit):
            CliArgParser(["run", "--api-port", "not_a_number"], "app").parse()

    def test_invalid_sim_port_type(self) -> None:
        with pytest.raises(SystemExit):
            CliArgParser(["sim", "--server-port", "not_a_number"], "app").parse()

    def test_invalid_log_level(self) -> None:
        with pytest.raises(SystemExit):
            CliArgParser(["run", "-l", "INVALID"], "app").parse()

    def test_missing_subcommand(self) -> None:
        with pytest.raises(SystemExit):
            CliArgParser([], "app").parse()
