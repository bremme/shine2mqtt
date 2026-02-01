import asyncio

from loguru import logger

from shine2mqtt.app.app import Application
from shine2mqtt.app.cli.converter import CliArgDictConverter
from shine2mqtt.app.cli.parser import CliArgParser
from shine2mqtt.app.config.config import ApplicationConfig
from shine2mqtt.app.config.file import ConfigFileLoader
from shine2mqtt.app.logger import LoggerConfigurator
from shine2mqtt.growatt.client.config import SimulatedClientConfig
from shine2mqtt.growatt.client.simulate import SimulatedClient
from shine2mqtt.growatt.protocol.frame.factory import FrameFactory


async def run_simulated_client(config: SimulatedClientConfig) -> None:
    decoder = FrameFactory.client_decoder()
    encoder = FrameFactory.encoder()
    client = SimulatedClient(encoder, decoder, config)
    await client.run()


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
            await run_simulated_client(config.simulated_client)
        else:
            await run_application(config)

    except asyncio.CancelledError:
        logger.info("Shutting down gracefully")
        raise


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by CTRL+C (Interrupted by user)")


if __name__ == "__main__":
    run()
