from loguru import logger
from shine2mqtt.growatt.protocol.messages import (
    BaseMessage,
)

from shine2mqtt.growatt.protocol.ack.encoder import AckPayloadEncoder
from shine2mqtt.growatt.protocol.announce.encoder import AnnouncePayloadEncoder
from shine2mqtt.growatt.protocol.base.encoder import PayloadEncoder
from shine2mqtt.growatt.protocol.data.encoder import (
    BufferedDataPayloadEncoder,
    DataPayloadEncoder,
)
from shine2mqtt.growatt.protocol.get_config.encoder import (
    GetConfigRequestPayloadEncoder,
    GetConfigResponsePayloadEncoder,
)
from shine2mqtt.growatt.protocol.ping.encoder import PingPayloadEncoder
from shine2mqtt.growatt.protocol.set_config.encoder import SetConfigRequestPayloadEncoder


class PayloadEncoderRegistry:
    def __init__(self):
        self._encoder: dict[type[BaseMessage], PayloadEncoder] = {}

    def register_encoder(
        self, encoder: PayloadEncoder, message_type: type[BaseMessage] | None = None
    ):
        """Register an encoder. If message_type is not provided, it will be extracted from encoder.message_type."""
        if message_type is None:
            message_type = encoder.message_type

        if message_type in self._encoder:
            message = f"Will overwrite existing encoder for message type: {message_type}"
            logger.warning(message)

        self._encoder[message_type] = encoder

    def get_encoder(self, message_type: type[BaseMessage]) -> PayloadEncoder:
        encoder = self._encoder.get(message_type, None)
        if encoder is None:
            message = f"No encoder registered for this message type: {message_type}"
            logger.error(message)
            raise KeyError(message)

        return encoder

    @classmethod
    def default(cls) -> PayloadEncoderRegistry:
        """Create a registry with all default encoders registered."""

        registry = cls()

        registry.register_encoder(AckPayloadEncoder())
        registry.register_encoder(PingPayloadEncoder())
        registry.register_encoder(AnnouncePayloadEncoder())
        registry.register_encoder(DataPayloadEncoder())
        registry.register_encoder(BufferedDataPayloadEncoder())
        registry.register_encoder(GetConfigRequestPayloadEncoder())
        registry.register_encoder(SetConfigRequestPayloadEncoder())
        registry.register_encoder(GetConfigResponsePayloadEncoder())

        return registry
