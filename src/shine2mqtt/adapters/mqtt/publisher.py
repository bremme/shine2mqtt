import asyncio
from dataclasses import asdict

import aiomqtt

from shine2mqtt.adapters.hass.discovery_mapper import HassDiscoveryMapper
from shine2mqtt.adapters.mqtt.mapper import MqttEventMapper
from shine2mqtt.adapters.mqtt.message import MqttMessage
from shine2mqtt.domain.events.events import (
    DataloggerAnnouncedEvent,
    DomainEvent,
    InverterStateUpdatedEvent,
)
from shine2mqtt.util.logger import logger


class MqttPublisher:
    def __init__(
        self,
        domain_events: asyncio.Queue[DomainEvent],
        mapper: MqttEventMapper,
        discovery: HassDiscoveryMapper,
    ):
        self._domain_events = domain_events
        self._event_mapper = mapper
        self._discovery_mapper = discovery

    async def run(self, client: aiomqtt.Client) -> None:
        while True:
            event = await self._domain_events.get()
            logger.info(
                f"Processing incoming {type(event).__name__} from '{event.datalogger_serial}' datalogger"
            )

            for message in self._map_event_to_message(event):
                logger.info(f"→ Publishing MQTT message to '{message.topic}'")
                await client.publish(**asdict(message))

    async def flush(self, client: aiomqtt.Client) -> None:
        logger.info("MQTT bridge shutting down, flushing Event → MQTT queue")
        while not self._domain_events.empty():
            event = self._domain_events.get_nowait()
            try:
                for message in self._map_event_to_message(event):
                    logger.info(f"→ Publishing MQTT message to '{message.topic}'")
                    await client.publish(**asdict(message), timeout=0.5)
            except Exception as e:
                logger.warning(f"Failed to publish message during flush: {e}")

    def _map_event_to_message(self, event: DomainEvent) -> list[MqttMessage]:
        match event:
            case DataloggerAnnouncedEvent():
                return self._discovery_mapper.get_discovery_messages(
                    event
                ) + self._event_mapper.map_datalogger_announced(event)
            case InverterStateUpdatedEvent():
                return self._event_mapper.map_inverter_state(event)
            case _:
                logger.debug(f"No handler for event type {type(event)}")
                return []
