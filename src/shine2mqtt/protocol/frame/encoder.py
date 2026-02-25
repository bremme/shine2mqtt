from shine2mqtt.protocol.frame.cipher import PayloadCipher
from shine2mqtt.protocol.frame.constants import ENCRYPTION_KEY
from shine2mqtt.protocol.frame.crc.calculator import CRCCalculator
from shine2mqtt.protocol.frame.crc.constants import CRC16_LENGTH
from shine2mqtt.protocol.frame.crc.encoder import CRCEncoder
from shine2mqtt.protocol.frame.header.encoder import HeaderEncoder
from shine2mqtt.protocol.frame.header.header import MBAPHeader
from shine2mqtt.protocol.messages.encoder.registry import PayloadEncoderRegistry
from shine2mqtt.protocol.messages.message import BaseMessage


class FrameEncoderFactory:
    """Factory for creating frame encoder and decoder with all dependencies."""

    @staticmethod
    def encoder() -> FrameEncoder:
        """Create a FrameEncoder with all default encoders registered."""
        return FrameEncoder(
            encryption_key=ENCRYPTION_KEY,
            header_encoder=HeaderEncoder(),
            payload_cipher=PayloadCipher(),
            encoder_registry=PayloadEncoderRegistry.default(),
            crc_calculator=CRCCalculator(),
            crc_encoder=CRCEncoder(),
        )


class FrameEncoder:
    def __init__(
        self,
        encryption_key: bytes,
        header_encoder: HeaderEncoder,
        payload_cipher: PayloadCipher,
        encoder_registry: PayloadEncoderRegistry,
        crc_calculator: CRCCalculator,
        crc_encoder: CRCEncoder,
    ):
        self.encryption_key = encryption_key
        self.header_encoder = header_encoder
        self.payload_cipher = payload_cipher
        self.encoder_registry = encoder_registry
        self.crc_calculator = crc_calculator
        self.crc_encoder = crc_encoder

    def encode(self, message: BaseMessage) -> bytes:
        encoder = self.encoder_registry.get_encoder(type(message))

        raw_payload = encoder.encode(message)

        # FIXME maybe not ideal to change header here
        # would be better to have immutability
        message.header.length = len(raw_payload) + CRC16_LENGTH

        return self.encode_frame(message.header, raw_payload)

    def encode_frame(self, header: MBAPHeader, payload: bytes) -> bytes:
        raw_header = self.header_encoder.encode(header)

        encrypted_payload = self.payload_cipher.encrypt(payload, self.encryption_key)

        crc = self.crc_calculator.calculate_crc16(raw_header + encrypted_payload)

        frame = raw_header + encrypted_payload + self.crc_encoder.encode(crc)

        return frame
