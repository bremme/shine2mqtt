import logging
from argparse import ArgumentParser, HelpFormatter, Namespace
from collections.abc import Sequence
from pathlib import Path


class CustomHelpFormatter(HelpFormatter):
    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=60, width=100)


class ArgParser:
    def __init__(self):
        parser = ArgumentParser(description="Shine2MQTT CLI", formatter_class=CustomHelpFormatter)

        subparsers = parser.add_subparsers(dest="subcommand")

        run_parser = subparsers.add_parser(
            "run", description="Run the Shine2MQTT server", formatter_class=CustomHelpFormatter
        )
        run_parser.set_defaults(simulated_client__enabled=False)

        sim_parser = subparsers.add_parser(
            "sim",
            description="Run a simulated Shine Wifi-X client",
            formatter_class=CustomHelpFormatter,
        )
        sim_parser.set_defaults(simulated_client__enabled=True)

        self._add_top_level_args(parser)

        self._add_capture_data_args(run_parser)
        self._add_mqtt_args(run_parser)
        self._add_server_args(run_parser)
        self._add_api_args(run_parser)

        self._add_simulated_client_args(sim_parser)

        self.parser = parser

    def _add_top_level_args(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-l",
            "--log-level",
            help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR)",
            choices=list(logging.getLevelNamesMapping().keys()),
            type=str,
            dest="log_level",
        )
        parser.add_argument(
            "--log-color",
            help="Enable colored logging output",
            action="store_true",
            default=None,
            dest="log_color",
        )

        parser.add_argument("-c", "--config-file", type=Path)

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
            help="Enable RESTTful API",
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

    def parse(self, argv: Sequence[str] | None = None) -> Namespace:
        return self.parser.parse_args(argv)
