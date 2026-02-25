import asyncio

from shine2mqtt.infrastructure.client.client import SimulatedClient
from shine2mqtt.infrastructure.client.transport import TCPTransport
from shine2mqtt.main.app import Application
from shine2mqtt.main.cli.converter import CliArgDictConverter
from shine2mqtt.main.cli.parser import CliArgParser
from shine2mqtt.main.config.config import ApplicationConfig
from shine2mqtt.main.config.file import ConfigFileLoader
from shine2mqtt.main.logger import LoggerConfigurator
from shine2mqtt.protocol.frame.factory import FrameFactory
from shine2mqtt.protocol.simulator.config import SimulatedClientConfig
from shine2mqtt.protocol.simulator.factory import ClientProtocolSessionFactory
from shine2mqtt.protocol.simulator.generator import FrameGenerator
from shine2mqtt.protocol.simulator.handler import ClientMessageHandler
from shine2mqtt.util.clock import MonotonicClockService
from shine2mqtt.util.logger import logger


async def run_simulated_datalogger(config: SimulatedClientConfig) -> None:
    transport = TCPTransport()

    encoder = FrameFactory.encoder()
    decoder = FrameFactory.client_decoder()
    clock = MonotonicClockService()

    generator = FrameGenerator(encoder=encoder)
    message_handler = ClientMessageHandler(generator=generator)
    session_factory = ClientProtocolSessionFactory(
        decoder=decoder,
        config=config,
        clock=clock,
        generator=generator,
        message_handler=message_handler,
    )
    datalogger = SimulatedClient(transport, session_factory, config)
    await datalogger.run()


async def run_application(config: ApplicationConfig) -> None:
    app = Application(config=config)
    await app.run()


def load_config() -> ApplicationConfig:
    args = CliArgParser.create().parse()

    file_config = ConfigFileLoader.create().load(args.config_file)
    cli_config = CliArgDictConverter.convert(args)

    return ApplicationConfig.create(file_config, cli_config)


def setup_logging(config: ApplicationConfig) -> None:
    LoggerConfigurator.setup(log_level=config.log_level, color=config.log_color)


async def main():
    try:
        config = load_config()

        setup_logging(config)

        logger.info(f"Loaded configuration: {config}")

        if config.simulated_client.enabled:
            await run_simulated_datalogger(config.simulated_client)
        else:
            await run_application(config)

    except asyncio.CancelledError:
        logger.info("Shutting down gracefully")
        raise


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Application stopped by CTRL+C (Interrupted by user)")


if __name__ == "__main__":
    run()
