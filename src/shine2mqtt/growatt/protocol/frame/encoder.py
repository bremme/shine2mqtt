from shine2mqtt.growatt.protocol.base.encoder_registry import PayloadEncoderRegistry
from shine2mqtt.growatt.protocol.base.message import BaseMessage
from shine2mqtt.growatt.protocol.crc.encoder import CRCEncoder
from shine2mqtt.growatt.protocol.frame.cipher import PayloadCipher
from shine2mqtt.growatt.protocol.frame.crc import CRC16_LENGTH, CRCCalculator
from shine2mqtt.growatt.protocol.header.encoder import HeaderEncoder
from shine2mqtt.growatt.protocol.header.header import MBAPHeader


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

        return self.encode_frame(message.header, raw_payload)

    def encode_frame(self, header: MBAPHeader, payload: bytes) -> bytes:
        # FIXME maybe not ideal to change message here
        # would be better to have immutability
        header.length = len(payload) + CRC16_LENGTH

        raw_header = self.header_encoder.encode(header)

        encrypted_payload = self.payload_cipher.encrypt(payload, self.encryption_key)

        crc = self.crc_calculator.calculate_crc16(raw_header + encrypted_payload)

        frame = raw_header + encrypted_payload + self.crc_encoder.encode(crc)

        return frame
