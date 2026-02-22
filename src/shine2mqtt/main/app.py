import asyncio
from pathlib import Path

import uvicorn

from shine2mqtt.adapters.api.api import create_app
from shine2mqtt.adapters.hass.discovery import HassDiscoveryPayloadBuilder
from shine2mqtt.adapters.hass.discovery_mapper import HassDiscoveryMapper
from shine2mqtt.adapters.hass.map import DATALOGGER_SENSOR_MAP, INVERTER_SENSOR_MAP
from shine2mqtt.adapters.mqtt.bridge import MqttBridge
from shine2mqtt.adapters.mqtt.client import MqttClient
from shine2mqtt.adapters.mqtt.mapper import MqttEventMapper
from shine2mqtt.adapters.mqtt.publisher import MqttPublisher
from shine2mqtt.adapters.mqtt.subscriber import MqttSubscriber
from shine2mqtt.app.handlers.read_register import ReadRegisterHandler
from shine2mqtt.app.handlers.send_raw_frame import SendRawFrameHandler
from shine2mqtt.app.handlers.write_register import WriteRegisterHandler
from shine2mqtt.domain.events.events import DomainEvents
from shine2mqtt.domain.interfaces.registry import SessionRegistry
from shine2mqtt.infrastructure.server.server import TCPServer
from shine2mqtt.main.config.config import ApplicationConfig
from shine2mqtt.protocol.frame.capturer import CaptureHandler
from shine2mqtt.protocol.frame.factory import FrameFactory
from shine2mqtt.protocol.session.factory import ProtocolSessionFactory
from shine2mqtt.protocol.session.registry import ProtocolSessionRegistry
from shine2mqtt.protocol.settings.registry import SettingsRegistry
from shine2mqtt.util.logger import logger


class Application:
    def __init__(self, config: ApplicationConfig):
        self.config = config

        domain_events = DomainEvents(maxsize=100)
        session_registry = ProtocolSessionRegistry()

        # Protocol
        encoder = FrameFactory.encoder()

        if config.capture_data:
            logger.info("Frame data capturing is enabled.")
            capture_handler = CaptureHandler.create(Path("./captured_frames"), encoder)
            decoder = FrameFactory.server_decoder(on_decode=capture_handler)
        else:
            decoder = FrameFactory.server_decoder()

        session_factory = ProtocolSessionFactory(
            encoder=encoder, decoder=decoder, domain_events=domain_events
        )

        # Infrastructure
        self._tcp_server = TCPServer(
            session_registry=session_registry,
            session_factory=session_factory,
            config=config.server,
        )

        # Adapters
        self._mqtt_bridge = self._setup_mqtt_bridge(domain_events, config)
        self._api_server = self._setup_api_server(session_registry, config)

    def _setup_mqtt_bridge(
        self, domain_events: DomainEvents, config: ApplicationConfig
    ) -> MqttBridge:
        discovery_builder = HassDiscoveryPayloadBuilder(
            config=config.mqtt.discovery,
            datalogger_sensor_map=DATALOGGER_SENSOR_MAP,
            inverter_sensor_map=INVERTER_SENSOR_MAP,
        )

        mapper = MqttEventMapper(config=config.mqtt)
        discovery = HassDiscoveryMapper(
            discovery=discovery_builder,
            enabled=config.mqtt.discovery.enabled,
        )
        publisher = MqttPublisher(
            domain_events=domain_events,
            mapper=mapper,
            discovery=discovery,
        )
        subscriber = MqttSubscriber()
        will_message = mapper.map_availability(online=False)
        mqtt_client = MqttClient(config.mqtt.server, will_message=will_message)

        return MqttBridge(
            client=mqtt_client,
            publisher=publisher,
            subscriber=subscriber,
            mapper=mapper,
        )

    def _setup_api_server(
        self, session_registry: SessionRegistry, config: ApplicationConfig
    ) -> uvicorn.Server | None:
        if not config.api.enabled:
            return None

        # Application handlers
        settings_registry = SettingsRegistry()
        read_handler = ReadRegisterHandler(session_registry, settings_registry)
        write_handler = WriteRegisterHandler(session_registry, settings_registry)
        send_raw_frame_handler = SendRawFrameHandler(session_registry)

        self._api_app = create_app(
            session_registry, read_handler, write_handler, send_raw_frame_handler
        )

        uvicorn_config = uvicorn.Config(
            app=self._api_app,
            host=config.api.host,
            port=config.api.port,
            loop="asyncio",
            log_config=None,
            log_level=None,
        )
        return uvicorn.Server(config=uvicorn_config)

    async def run(self):
        tasks = [
            asyncio.create_task(self._tcp_server.serve()),
            asyncio.create_task(self._mqtt_bridge.run()),
        ]

        if self.config.api.enabled and self._api_server is not None:
            tasks.append(asyncio.create_task(self._api_server.serve()))

        await asyncio.gather(*tasks)
