import logging
import sys
from argparse import ArgumentParser, HelpFormatter, Namespace
from collections.abc import Sequence
from pathlib import Path

from shine2mqtt import NAME


class _CustomHelpFormatter(HelpFormatter):
    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=60, width=120)


class CliArgParser:
    def __init__(self, argv: Sequence[str], prog: str):
        self.argv = argv
        self.prog = prog

        self.parser = self._create_parsers()

    @staticmethod
    def create() -> CliArgParser:
        return CliArgParser(sys.argv[1:], prog=NAME)

    def _create_parsers(self) -> ArgumentParser:
        parser = ArgumentParser(
            prog=self.prog,
            description="Shine2MQTT acts as a local server for your Growatt Shine (Wifi-X) datalogger, capturing data that would normally be sent to Growatt's cloud servers. It publishes this data via MQTT in a Home Assistant-friendly format, giving you complete local control of your solar inverter data.",
            formatter_class=_CustomHelpFormatter,
        )

        subparsers = parser.add_subparsers(required=True)

        run_parser = subparsers.add_parser(
            "run",
            help="Run the Shine2MQTT server (use 'shine2mqtt run --help' for more info)",
            description="Run the Shine2MQTT server",
            formatter_class=_CustomHelpFormatter,
            prog=self.prog,
        )
        run_parser.set_defaults(simulated_client__enabled=False)

        sim_parser = subparsers.add_parser(
            "sim",
            help="Simulate a Shine Wifi-X client (use 'shine2mqtt sim --help' for more info)",
            description="Simulate a Shine Wifi-X client. Send data to a Shine2MQTT server, for testing purposes.",
            formatter_class=_CustomHelpFormatter,
            prog=self.prog,
        )
        sim_parser.set_defaults(simulated_client__enabled=True)

        self._add_top_level_args(parser)

        self._add_run_args(run_parser)

        self._add_simulated_client_args(sim_parser)

        return parser

    def _add_top_level_args(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-l",
            "--log-level",
            help="Set the logging level (e.g. DEBUG, INFO, WARNING, ERROR)",
            choices=list(logging.getLevelNamesMapping().keys()),
            type=str,
            dest="log_level",
            metavar="LEVEL",
        )
        parser.add_argument(
            "-C",
            "--log-color",
            help="Enable or disable colored logging output",
            action="store_true",
            default=None,
            dest="log_color",
        )

        parser.add_argument(
            "-c",
            "--config-file",
            help="Path to configuration file",
            type=Path,
            dest="config_file",
            metavar="FILE",
        )

    def _add_run_args(self, parser: ArgumentParser) -> None:
        self._add_capture_data_args(parser)
        self._add_mqtt_args(parser)
        self._add_server_args(parser)
        self._add_api_args(parser)

    def _add_capture_data_args(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--capture-data",
            help="Enable capturing of raw Modbus TCP frames",
            action="store_true",
            default=None,
            dest="capture_data",
        )

    def _add_mqtt_args(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--mqtt-base-topic", help="Base MQTT topic", dest="mqtt__base_topic", metavar="TOPIC"
        )
        parser.add_argument(
            "--mqtt-availability-topic",
            help="MQTT availability topic",
            dest="mqtt__availability_topic",
            metavar="TOPIC",
        )

        parser.add_argument(
            "--mqtt-host", help="MQTT server host", dest="mqtt__server__host", metavar="HOST"
        )
        parser.add_argument(
            "--mqtt-port",
            type=int,
            help="MQTT server port",
            dest="mqtt__server__port",
            metavar="PORT",
        )
        parser.add_argument(
            "--mqtt-username",
            help="MQTT username",
            dest="mqtt__server__username",
            metavar="USERNAME",
        )
        parser.add_argument(
            "--mqtt-password",
            help="MQTT password",
            dest="mqtt__server__password",
            metavar="PASSWORD",
        )

        parser.add_argument(
            "--mqtt-discovery",
            action="store_true",
            help="Enable MQTT (Home Assistant) auto discovery",
            default=None,
            dest="mqtt__discovery__enabled",
        )
        parser.add_argument(
            "--mqtt-discovery-inverter",
            help="Inverter model (e.g. MIC 3000TL-X)",
            dest="mqtt__discovery__inverter__model",
            metavar="INVERTER",
        )
        parser.add_argument(
            "--mqtt-discovery-datalogger",
            help="Datalogger model (e.g. Shine Wifi-X)",
            dest="mqtt__discovery__datalogger__model",
            metavar="DATALOGGER",
        )

    def _add_server_args(self, parser: ArgumentParser) -> None:
        parser.add_argument("--server-host", help="Server listen address", dest="server__host")
        parser.add_argument(
            "--server-port", type=int, help="Server listen port", dest="server__port"
        )

    def _add_api_args(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--api",
            help="Enable RESTfull API",
            action="store_true",
            default=None,
            dest="api__enabled",
        )
        parser.add_argument(
            "--api-host", help="API listen address", dest="api__host", metavar="HOST"
        )
        parser.add_argument(
            "--api-port", type=int, help="API listen port", dest="api__port", metavar="PORT"
        )

    def _add_simulated_client_args(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--server-host",
            help="Server host",
            dest="simulated_client__server_host",
            metavar="HOST",
        )
        parser.add_argument(
            "--server-port",
            type=int,
            help="Server port",
            dest="simulated_client__server_port",
            metavar="PORT",
        )

    def parse(self) -> Namespace:
        return self.parser.parse_args(self.argv)
