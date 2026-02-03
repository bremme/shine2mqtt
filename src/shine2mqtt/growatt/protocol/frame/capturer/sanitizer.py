from dataclasses import replace

from shine2mqtt.growatt.protocol.constants import (
    DATALOGGER_IP_ADDRESS_REGISTER,
    DATALOGGER_MAC_ADDRESS_REGISTER,
    DATALOGGER_SERVER_IP_ADDRESS_REGISTER,
    DATALOGGER_WIFI_PASSWORD_REGISTER,
    DATALOGGER_WIFI_SSID_REGISTER,
    ENCRYPTION_KEY,
    FunctionCode,
)
from shine2mqtt.growatt.protocol.decoders.decoder import ByteDecoder
from shine2mqtt.growatt.protocol.encoders.crc import CRCEncoder
from shine2mqtt.growatt.protocol.encoders.encoder import ByteEncoder
from shine2mqtt.growatt.protocol.encoders.header import HeaderEncoder
from shine2mqtt.growatt.protocol.frame.cipher import PayloadCipher
from shine2mqtt.growatt.protocol.frame.crc import CRC16_LENGTH, CRCCalculator
from shine2mqtt.growatt.protocol.messages.announce import GrowattAnnounceMessage
from shine2mqtt.growatt.protocol.messages.base import BaseMessage
from shine2mqtt.growatt.protocol.messages.config import GrowattGetConfigResponseMessage
from shine2mqtt.growatt.protocol.messages.data import GrowattBufferedDataMessage, GrowattDataMessage
from shine2mqtt.growatt.protocol.messages.header import MBAPHeader
from shine2mqtt.growatt.protocol.messages.ping import GrowattPingMessage

DUMMY_DATALOGGER_SERIAL = "XGDABCDEFG"
DUMMY_INVERTER_SERIAL = "MLG0A12345"
DUMMY_IP_ADDRESS = "1.2.3.4"
DUMMY_MAC_ADDRESS = "00:11:22:33:44:55"
DUMMY_SERVER_IP_ADDRESS = "5.6.7.8"
DUMMY_WIFI_SSID = "MyWiFiNetwork"
DUMMY_WIFI_PASSWORD = "MySecretPassword"

SENSITIVE_CONFIG_REGISTER_MAP = {
    DATALOGGER_IP_ADDRESS_REGISTER: DUMMY_IP_ADDRESS,
    DATALOGGER_MAC_ADDRESS_REGISTER: DUMMY_MAC_ADDRESS,
    DATALOGGER_SERVER_IP_ADDRESS_REGISTER: DUMMY_SERVER_IP_ADDRESS,
    DATALOGGER_WIFI_PASSWORD_REGISTER: DUMMY_WIFI_PASSWORD,
    DATALOGGER_WIFI_SSID_REGISTER: DUMMY_WIFI_SSID,
}


class RawPayloadSanitizer:
    def __init__(
        self,
        encryption_key: bytes,
        header_encoder: HeaderEncoder,
        payload_cipher: PayloadCipher,
        crc_calculator: CRCCalculator,
        crc_encoder: CRCEncoder,
    ):
        self.encryption_key = encryption_key
        self.header_encoder = header_encoder
        self.payload_cipher = payload_cipher
        self.crc_calculator = crc_calculator
        self.crc_encoder = crc_encoder

    @staticmethod
    def create():
        return RawPayloadSanitizer(
            encryption_key=ENCRYPTION_KEY,
            header_encoder=HeaderEncoder(),
            payload_cipher=PayloadCipher(),
            crc_calculator=CRCCalculator(),
            crc_encoder=CRCEncoder(),
        )

    def sanitize(self, header: MBAPHeader, payload: bytes) -> tuple[bytes, MBAPHeader, bytes]:
        sanitized_payload = self._sanitize_payload(header.function_code, payload)

        sanitized_header = replace(header, length=len(sanitized_payload) + CRC16_LENGTH)

        raw_header = self.header_encoder.encode(sanitized_header)

        encrypted_payload = self.payload_cipher.encrypt(sanitized_payload, self.encryption_key)

        crc = self.crc_calculator.calculate_crc16(raw_header + encrypted_payload)

        sanitized_frame = raw_header + encrypted_payload + self.crc_encoder.encode(crc)

        return sanitized_frame, sanitized_header, sanitized_payload

    def _sanitize_payload(self, function_code: FunctionCode, payload: bytes) -> bytes:
        match function_code:
            case FunctionCode.ANNOUNCE | FunctionCode.BUFFERED_DATA | FunctionCode.DATA:
                return self._sanitize_announce_or_data_payload(payload)
            case FunctionCode.GET_CONFIG:
                return self._sanitize_get_config_response_payload(payload)
            case FunctionCode.PING:
                return self._sanitize_ping_payload(payload)
            case _:
                return payload

        return payload

    def _sanitize_announce_or_data_payload(self, payload: bytes) -> bytes:
        sanitized_payload = bytearray(payload)
        sanitized_payload[0:10] = ByteEncoder.encode_str(DUMMY_DATALOGGER_SERIAL, 10)
        sanitized_payload[30:40] = ByteEncoder.encode_str(DUMMY_INVERTER_SERIAL, 10)
        return bytes(sanitized_payload)

    def _sanitize_get_config_response_payload(self, payload: bytes) -> bytes:
        sanitized_payload = bytearray(payload)
        sanitized_payload[0:10] = ByteEncoder.encode_str(DUMMY_DATALOGGER_SERIAL, 10)

        register = ByteDecoder.decode_u16(payload, 30)

        if register not in SENSITIVE_CONFIG_REGISTER_MAP:
            return bytes(sanitized_payload)

        sanitized_value = SENSITIVE_CONFIG_REGISTER_MAP[register]

        new_length = len(sanitized_value)
        sanitized_payload[32:34] = ByteEncoder.encode_u16(new_length)
        sanitized_payload[34 : 34 + len(sanitized_value)] = ByteEncoder.encode_str(
            sanitized_value, new_length
        )

        return bytes(sanitized_payload)

    def _sanitize_ping_payload(self, payload: bytes) -> bytes:
        sanitized_payload = bytearray(payload)
        sanitized_payload[0:10] = ByteEncoder.encode_str(DUMMY_DATALOGGER_SERIAL, 10)
        return bytes(sanitized_payload)


class MessageSanitizer:
    def sanitize(self, message: BaseMessage) -> BaseMessage:
        match message:
            case GrowattAnnounceMessage():
                return replace(
                    message,
                    datalogger_serial=DUMMY_DATALOGGER_SERIAL,
                    inverter_serial=DUMMY_INVERTER_SERIAL,
                )
            case GrowattBufferedDataMessage() | GrowattDataMessage():
                return replace(
                    message,
                    datalogger_serial=DUMMY_DATALOGGER_SERIAL,
                    inverter_serial=DUMMY_INVERTER_SERIAL,
                )
            case GrowattPingMessage():
                return replace(
                    message,
                    datalogger_serial=DUMMY_DATALOGGER_SERIAL,
                )
            case GrowattGetConfigResponseMessage():
                return self._sanitize_get_config_response(message)

        return message

    def _sanitize_get_config_response(
        self, message: GrowattGetConfigResponseMessage
    ) -> GrowattGetConfigResponseMessage:
        sanitized_registers = {
            "ip_address": DUMMY_IP_ADDRESS,
            "mac_address": DUMMY_MAC_ADDRESS,
            "server_ip_address": DUMMY_SERVER_IP_ADDRESS,
            "wifi_ssid": DUMMY_WIFI_SSID,
            "wifi_password": DUMMY_WIFI_PASSWORD,
        }
        if message.name not in sanitized_registers:
            return message

        sanitized_value = sanitized_registers[message.name]

        sanitized_data = sanitized_value.encode("ascii")
        length_difference = len(sanitized_data) - len(message.data)

        return replace(
            message,
            datalogger_serial=DUMMY_DATALOGGER_SERIAL,
            length=message.length + length_difference,
            data=sanitized_data,
            value=sanitized_value,
        )
