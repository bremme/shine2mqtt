import asyncio

from shine2mqtt.growatt.protocol.messages.base import BaseMessage
from shine2mqtt.growatt.protocol.processor.command.command import BaseCommand

IncomingFrames = asyncio.Queue[bytes]
OutgoingFrames = asyncio.Queue[bytes]
ProtocolCommands = asyncio.Queue[BaseCommand]
ProtocolEvents = asyncio.Queue[BaseMessage]
