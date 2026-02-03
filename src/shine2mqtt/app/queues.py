import asyncio

from shine2mqtt.growatt.protocol.processor.command.command import BaseCommand
from shine2mqtt.growatt.protocol.messages.base import BaseMessage

IncomingFrames = asyncio.Queue[bytes]
OutgoingFrames = asyncio.Queue[bytes]
ProtocolCommands = asyncio.Queue[BaseCommand]
ProtocolEvents = asyncio.Queue[BaseMessage]
