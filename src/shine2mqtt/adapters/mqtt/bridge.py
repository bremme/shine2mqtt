import asyncio
from dataclasses import asdict

import aiomqtt

from shine2mqtt.adapters.mqtt.client import MqttClient
from shine2mqtt.adapters.mqtt.mapper import MqttEventMapper
from shine2mqtt.adapters.mqtt.publisher import MqttPublisher
from shine2mqtt.adapters.mqtt.subscriber import MqttSubscriber
from shine2mqtt.util.logger import logger


class MqttBridge:
    _RECONNECT_INTERVAL = 5

    def __init__(
        self,
        client: MqttClient,
        publisher: MqttPublisher,
        subscriber: MqttSubscriber,
        mapper: MqttEventMapper,
    ):
        self._client = client
        self._publisher = publisher
        self._subscriber = subscriber
        self._event_mapper = mapper

    async def run(self):
        while True:
            try:
                async with self._client.connect() as client:
                    logger.info("Connected to MQTT broker")
                    try:
                        await client.publish(
                            **asdict(self._event_mapper.map_availability(online=True))
                        )
                        await asyncio.gather(
                            self._publisher.run(client),
                            self._subscriber.run(client),
                        )
                    except asyncio.CancelledError:
                        await self._publisher.flush(client)
                        await client.publish(
                            **asdict(self._event_mapper.map_availability(online=False))
                        )
                        raise
            except aiomqtt.MqttError as error:
                logger.error(
                    f"MQTT connection error: {error}. "
                    f"Reconnecting in {self._RECONNECT_INTERVAL} seconds..."
                )
                await asyncio.sleep(self._RECONNECT_INTERVAL)
