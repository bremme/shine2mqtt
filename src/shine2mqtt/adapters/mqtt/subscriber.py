import aiomqtt

from shine2mqtt.util.logger import logger


class MqttSubscriber:
    async def run(self, client: aiomqtt.Client) -> None:
        async for message in client.messages:
            logger.debug(f"Received MQTT message '{message.topic}': {message.payload}")
