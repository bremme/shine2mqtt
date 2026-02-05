import asyncio
from pathlib import Path

import uvicorn
from loguru import logger

from shine2mqtt.api.api import RestApi
from shine2mqtt.app.config.config import ApplicationConfig
from shine2mqtt.app.queues import (
    ProtocolCommands,
    ProtocolEvents,
)
from shine2mqtt.growatt.protocol.config import ConfigRegistry
from shine2mqtt.growatt.protocol.frame import (
    FrameFactory,
)
from shine2mqtt.growatt.protocol.frame.capturer import CaptureHandler
from shine2mqtt.growatt.protocol.session.registry import ProtocolSessionRegistry
from shine2mqtt.growatt.protocol.session.session import ProtocolSessionFactory
from shine2mqtt.growatt.server import GrowattServer
from shine2mqtt.hass.discovery import MqttDiscoveryBuilder
from shine2mqtt.mqtt.bridge import MqttBridge
from shine2mqtt.mqtt.client import MqttClient
from shine2mqtt.mqtt.processor import MqttDataloggerMessageProcessor


class Application:
    def __init__(self, config: ApplicationConfig):
        self.config = config

        protocol_commands = ProtocolCommands(maxsize=100)
        protocol_events = ProtocolEvents(maxsize=100)

        encoder = FrameFactory.encoder()

        if config.capture_data:
            logger.info("Frame data capturing is enabled.")
            capture_handler = CaptureHandler.create(Path("./captured_frames"), encoder)
            decoder = FrameFactory.server_decoder(on_decode=capture_handler)
        else:
            decoder = FrameFactory.server_decoder()

        config_registry = ConfigRegistry()

        self.session_factory = ProtocolSessionFactory(
            decoder=decoder,
            encoder=encoder,
            config_registry=config_registry,
            protocol_events=protocol_events,
        )

        session_registry = ProtocolSessionRegistry()

        self.tcp_server = GrowattServer(
            config=config.server,
            session_factory=self.session_factory,
            session_registry=session_registry,
        )

        self.mqtt_bridge = self._setup_mqtt_bridge(protocol_events, config)

        self.rest_server = self._setup_rest_server(config, protocol_commands)

    def _setup_mqtt_bridge(
        self, protocol_events: ProtocolEvents, config: ApplicationConfig
    ) -> MqttBridge:
        discovery_builder = MqttDiscoveryBuilder(config=config.mqtt.discovery)

        mqtt_event_processor = MqttDataloggerMessageProcessor(
            discovery=discovery_builder, config=config.mqtt
        )
        will_message = mqtt_event_processor.build_availability_message(online=False)
        mqtt_client = MqttClient(config.mqtt.server, will_message=will_message)

        return MqttBridge(
            protocol_events=protocol_events,
            client=mqtt_client,
            event_processor=mqtt_event_processor,
        )

    def _setup_rest_server(
        self,
        config: ApplicationConfig,
        protocol_commands: ProtocolCommands,
    ):
        if not config.api.enabled:
            return None

        api_app = RestApi(protocol_commands=protocol_commands).app

        uvicorn_config = uvicorn.Config(
            app=api_app,
            host=config.api.host,
            port=config.api.port,
            loop="asyncio",
            log_config=None,
            log_level=None,
        )

        return uvicorn.Server(config=uvicorn_config)

    async def run(self):
        try:
            await self.tcp_server.start()

            tasks = [
                asyncio.create_task(self.tcp_server.serve()),
                # asyncio.create_task(self.coordinator.run()),
                asyncio.create_task(self.mqtt_bridge.run()),
            ]

            if self.config.api.enabled and self.rest_server is not None:
                tasks.append(asyncio.create_task(self.rest_server.serve()))

            await asyncio.gather(*tasks)

        finally:
            await self.tcp_server.stop()
