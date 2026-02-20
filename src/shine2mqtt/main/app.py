import asyncio

from shine2mqtt.adapters.hass.discovery import MqttDiscoveryBuilder
from shine2mqtt.adapters.hass.map import DATALOGGER_SENSOR_MAP, INVERTER_SENSOR_MAP
from shine2mqtt.adapters.mqtt.bridge import MqttBridge
from shine2mqtt.adapters.mqtt.client import MqttClient
from shine2mqtt.adapters.mqtt.mapper import MqttEventMapper
from shine2mqtt.domain.events.events import DomainEvent
from shine2mqtt.infrastructure.server.server import TCPServer
from shine2mqtt.main.config.config import ApplicationConfig
from shine2mqtt.protocol.frame.factory import FrameFactory
from shine2mqtt.protocol.session.registry import ProtocolSessionRegistry
from shine2mqtt.protocol.session.session import ProtocolSessionFactory


class Application:
    def __init__(self, config: ApplicationConfig):
        self.config = config

        domain_events = asyncio.Queue[DomainEvent](maxsize=100)

        encoder = FrameFactory.encoder()
        decoder = FrameFactory.server_decoder()
        session_registry = ProtocolSessionRegistry()
        session_factory = ProtocolSessionFactory(
            encoder=encoder, decoder=decoder, domain_events=domain_events
        )

        # Infrastructure
        tcp_server = TCPServer(
            session_registry=session_registry,
            session_factory=session_factory,
            config=config.server,
        )

        # Application handlers
        # read_handler = ReadRegisterHandler(session_registry)
        # write_handler = WriteRegisterHandler(session_registry)

        # Adapters
        # mqtt_publisher = MqttEventPublisher(event_queue, config)
        # mqtt_subscriber = MqttCommandSubscriber(write_handler)
        self._mqtt_bridge = self._setup_mqtt_bridge(domain_events, config)

        # api_app = create_api_app(read_handler, write_handler, session_registry)

        self._tcp_server = tcp_server
        # self._mqtt_bridge = mqtt_bridge
        # self._api_app = api_app

    def _setup_mqtt_bridge(
        self, domain_events: asyncio.Queue[DomainEvent], config: ApplicationConfig
    ) -> MqttBridge:
        discovery_builder = MqttDiscoveryBuilder(
            config=config.mqtt.discovery,
            datalogger_sensor_map=DATALOGGER_SENSOR_MAP,
            inverter_sensor_map=INVERTER_SENSOR_MAP,
        )

        mqtt_event_processor = MqttEventMapper(discovery=discovery_builder, config=config.mqtt)
        will_message = mqtt_event_processor.build_availability_message(online=False)
        mqtt_client = MqttClient(config.mqtt.server, will_message=will_message)

        return MqttBridge(
            domain_events=domain_events,
            client=mqtt_client,
            event_processor=mqtt_event_processor,
        )

    async def run(self):
        # try:
        # await self._tcp_server.start()

        tasks = [
            asyncio.create_task(self._tcp_server.serve()),
            asyncio.create_task(self._mqtt_bridge.run()),
        ]

        # if self.config.api.enabled and self.rest_server is not None:
        #     tasks.append(asyncio.create_task(self.rest_server.serve()))

        await asyncio.gather(*tasks)

        # finally:
        #     # self._tcp_server.stop()
        #     pass


# class Application:
#     def __init__(self, config: ApplicationConfig):
#         self.config = config

#         protocol_events = ProtocolEvents(maxsize=100)

#         encoder = FrameFactory.encoder()

#         if config.capture_data:
#             logger.info("Frame data capturing is enabled.")
#             capture_handler = CaptureHandler.create(Path("./captured_frames"), encoder)
#             decoder = FrameFactory.server_decoder(on_decode=capture_handler)
#         else:
#             decoder = FrameFactory.server_decoder()

#         config_registry = ConfigRegistry()

#         self.session_factory = ServerProtocolSessionFactory(
#             decoder=decoder,
#             encoder=encoder,
#             config_registry=config_registry,
#             protocol_events=protocol_events,
#         )

#         session_registry = ProtocolSessionRegistry()

#         self.tcp_server = GrowattServer(
#             config=config.server,
#             session_factory=self.session_factory,
#             session_registry=session_registry,
#         )

#         self.mqtt_bridge = self._setup_mqtt_bridge(protocol_events, config)

#         self.rest_server = self._setup_rest_server(config, session_registry)

#     def _setup_mqtt_bridge(
#         self, protocol_events: ProtocolEvents, config: ApplicationConfig
#     ) -> MqttBridge:
#         discovery_builder = MqttDiscoveryBuilder(
#             config=config.mqtt.discovery,
#             datalogger_sensor_map=DATALOGGER_SENSOR_MAP,
#             inverter_sensor_map=INVERTER_SENSOR_MAP,
#         )

#         mqtt_event_processor = MqttDataloggerMessageProcessor(
#             discovery=discovery_builder, config=config.mqtt
#         )
#         will_message = mqtt_event_processor.build_availability_message(online=False)
#         mqtt_client = MqttClient(config.mqtt.server, will_message=will_message)

#         return MqttBridge(
#             protocol_events=protocol_events,
#             client=mqtt_client,
#             event_processor=mqtt_event_processor,
#         )

#     def _setup_rest_server(
#         self,
#         config: ApplicationConfig,
#         session_registry: ProtocolSessionRegistry,
#     ):
#         if not config.api.enabled:
#             return None

#         api_app = create_app(session_registry=session_registry)

#         uvicorn_config = uvicorn.Config(
#             app=api_app,
#             host=config.api.host,
#             port=config.api.port,
#             loop="asyncio",
#             log_config=None,
#             log_level=None,
#         )

#         return uvicorn.Server(config=uvicorn_config)

#     async def run(self):
#         try:
#             await self.tcp_server.start()

#             tasks = [
#                 asyncio.create_task(self.tcp_server.serve()),
#                 asyncio.create_task(self.mqtt_bridge.run()),
#             ]

#             if self.config.api.enabled and self.rest_server is not None:
#                 tasks.append(asyncio.create_task(self.rest_server.serve()))

#             await asyncio.gather(*tasks)

#         finally:
#             await self.tcp_server.stop()
