from abc import ABC, abstractmethod

from shine2mqtt.protocol.codec.byte import ByteEncoder
from shine2mqtt.protocol.messages.message import BaseMessage


class PayloadEncoder[T: BaseMessage](ABC, ByteEncoder):
    def __init__(self, message_type: type[T]):
        self.message_type = message_type

    @abstractmethod
    def encode(self, message: T) -> bytes:
        pass
