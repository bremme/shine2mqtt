import asyncio
from dataclasses import asdict

import aiomqtt
from aiomqtt import Client

from shine2mqtt.adapters.mqtt.client import MqttClient
from shine2mqtt.adapters.mqtt.mapper import MqttEventMapper
from shine2mqtt.domain.events.events import DomainEvent
from shine2mqtt.util.logger import logger


class MqttBridge:
    _RECONNECT_INTERVAL = 5

    def __init__(
        self,
        domain_events: asyncio.Queue[DomainEvent],
        event_processor: MqttEventMapper,
        client: MqttClient,
    ):
        self._client = client
        self._domain_events = domain_events
        self._event_processor = event_processor

    async def run(self):
        while True:
            try:
                async with self._client.connect() as client:
                    logger.info("Connected to MQTT broker")
                    try:
                        await self._publish_availability_status(client, online=True)
                        await asyncio.gather(
                            self._subscriber(client),
                            self._publisher(client),
                        )
                    except asyncio.CancelledError:
                        await self._handle_shutdown(client)
                        raise
            except aiomqtt.MqttError as error:
                logger.error(
                    f"MQTT connection error: {error}. "
                    f"Reconnecting in {self._RECONNECT_INTERVAL} seconds..."
                )
                await asyncio.sleep(self._RECONNECT_INTERVAL)

    async def _publish_availability_status(self, client: Client, online: bool) -> None:
        mqtt_message = self._event_processor.build_availability_message(online)
        await client.publish(**asdict(mqtt_message))

    async def _handle_shutdown(self, client: Client) -> None:
        logger.info("MQTT bridge shutting down, flushing Event → MQTT queue")
        await self._flush_domain_events(client)
        await self._publish_availability_status(client, online=False)

    async def _publisher(self, client: Client) -> None:
        while True:
            event: DomainEvent = await self._domain_events.get()

            logger.info(
                f"Processing incoming {type(event).__name__} from '{event.datalogger_serial}' datalogger"
            )

            for mqtt_message in self._event_processor.process(event):
                logger.info(f"→ Publishing MQTT message to '{mqtt_message.topic}'")
                await client.publish(**asdict(mqtt_message))

    async def _subscriber(self, client: Client) -> None:
        async for msg in client.messages:
            logger.debug(f"Received MQTT message '{msg.topic}': {msg.payload}")

    async def _flush_domain_events(self, client: Client) -> None:
        while not self._domain_events.empty():
            event = self._domain_events.get_nowait()
            try:
                for mqtt_message in self._event_processor.process(event):
                    await client.publish(**asdict(mqtt_message), timeout=0.5)
            except Exception as e:
                logger.warning(f"Failed to publish message during flush: {e}")
