from collections.abc import Callable

from shine2mqtt.protocol.frame.cipher import PayloadCipher
from shine2mqtt.protocol.frame.constants import CRC_LENGTH, DECRYPTION_KEY, HEADER_LENGTH
from shine2mqtt.protocol.frame.crc.calculator import CRCCalculator
from shine2mqtt.protocol.frame.crc.decoder import CRCDecoder
from shine2mqtt.protocol.frame.header.decoder import HeaderDecoder
from shine2mqtt.protocol.frame.header.header import MBAPHeader
from shine2mqtt.protocol.frame.validator import FrameValidator
from shine2mqtt.protocol.messages.decoder.decoder import ByteDecoder, MessageDecoder
from shine2mqtt.protocol.messages.decoder.registry import DecoderRegistry
from shine2mqtt.protocol.messages.message import BaseMessage
from shine2mqtt.util.logger import logger


class DecodingError(Exception):
    pass


class FrameDecoderFactory:
    """Factory for creating frame encoder and decoder with all dependencies."""

    @staticmethod
    def decoder(on_decode=None, decoder_registry: DecoderRegistry | None = None) -> FrameDecoder:
        """Create a FrameDecoder with specified or default decoders registered.

        Args:
            on_decode: Optional callback(frame: bytes, message: BaseMessage) called after decoding
            decoder_registry: Optional decoder registry. Defaults to server registry if not specified.
        """
        crc_calculator = CRCCalculator()
        crc_decoder = CRCDecoder()

        return FrameDecoder(
            decryption_key=DECRYPTION_KEY,
            header_decoder=HeaderDecoder(),
            frame_validator=FrameValidator(crc_calculator, crc_decoder),
            payload_cipher=PayloadCipher(),
            decoder_registry=decoder_registry or DecoderRegistry.server(),
            on_decode=on_decode,
        )

    @staticmethod
    def server_decoder(on_decode=None) -> FrameDecoder:
        """Create a FrameDecoder for server (decodes messages FROM client).

        Args:
            on_decode: Optional callback(frame: bytes, message: BaseMessage) called after decoding
        """
        return FrameDecoderFactory.decoder(
            on_decode=on_decode, decoder_registry=DecoderRegistry.server()
        )

    @staticmethod
    def client_decoder(on_decode=None) -> FrameDecoder:
        """Create a FrameDecoder for client (decodes messages FROM server).

        Args:
            on_decode: Optional callback(frame: bytes, message: BaseMessage) called after decoding
        """
        return FrameDecoderFactory.decoder(
            on_decode=on_decode, decoder_registry=DecoderRegistry.client()
        )


class FrameDecoder:
    def __init__(
        self,
        decryption_key: bytes,
        header_decoder: HeaderDecoder,
        frame_validator: FrameValidator,
        payload_cipher: PayloadCipher,
        decoder_registry: DecoderRegistry,
        on_decode: Callable[[MBAPHeader, bytes], None] | None = None,
    ):
        self.decryption_key = decryption_key
        self.header_decoder = header_decoder
        self.validator = frame_validator
        self.payload_cipher = payload_cipher
        self.decoder_registry = decoder_registry
        self.on_decode = on_decode

    @staticmethod
    def extract_payload_length(raw_header: bytes) -> int:
        return ByteDecoder.decode_u16(raw_header, 4)

    def decode_header(self, raw_header: bytes) -> MBAPHeader:
        return self.header_decoder.decode(raw_header)

    def decode(self, frame: bytes) -> BaseMessage:
        header: MBAPHeader = self.decode_header(frame[:HEADER_LENGTH])
        self.validator.validate(frame, header)

        encrypted_payload = frame[HEADER_LENGTH : HEADER_LENGTH + header.length - CRC_LENGTH]

        raw_payload = self.payload_cipher.decrypt(encrypted_payload, self.decryption_key)

        try:
            decoder: MessageDecoder = self.decoder_registry.get_decoder(header.function_code)
        except KeyError as e:
            message = f"Decoder not found for function code {header.function_code.name} ({header.function_code.value:#02x})"
            logger.error(message)
            raise DecodingError(message) from e

        try:
            message = decoder.decode(header, raw_payload)

            # Hook: capture frame after successful decode
            try:
                if self.on_decode:
                    self.on_decode(header, raw_payload)
            except Exception as e:
                logger.error(f"on_decode hook failed: {e}")

            return message
        except Exception as e:
            message = f"Failed to decode message with function code {header.function_code.name} ({header.function_code.value:#02x}) {e}"
            logger.error(message)
            raise DecodingError(message) from e
