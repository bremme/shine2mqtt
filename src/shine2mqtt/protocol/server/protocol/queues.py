import asyncio

from shine2mqtt.protocol.server.protocol.event import ProtocolEvent
from shine2mqtt.protocol.server.protocol.session.command.command import BaseCommand

IncomingFrames = asyncio.Queue[bytes]
OutgoingFrames = asyncio.Queue[bytes]
ProtocolCommands = asyncio.Queue[BaseCommand]
ProtocolEvents = asyncio.Queue[ProtocolEvent]
