import asyncio
from asyncio import StreamReader, StreamWriter

from loguru import logger

from shine2mqtt.app.queues import OutgoingFrames
from shine2mqtt.growatt.protocol.frame.decoder import HEADER_LENGTH, FrameDecoder
from shine2mqtt.growatt.protocol.session.session import ProtocolSession


class GrowattTcpSession:
    def __init__(
        self,
        reader: StreamReader,
        writer: StreamWriter,
        # incoming_frames: IncomingFrames,
        outgoing_frames: OutgoingFrames,
        protocol_session: ProtocolSession,
    ):
        self.reader = reader
        self.writer = writer

        # self._incoming_frames = incoming_frames
        self._outgoing_frames = outgoing_frames
        self._protocol_session = protocol_session

    async def run(self):
        try:
            await asyncio.gather(self._reader_loop(), self._writer_loop())
        finally:
            logger.info("Closing TCP session")
            await self._flush_writer_queue()
            self.writer.close()
            await self.writer.wait_closed()
            logger.info("TCP session fully closed")

    async def _reader_loop(self):
        logger.info("Starting TCP Session reader loop, waiting for messages")
        try:
            while True:
                raw_header = await self.reader.readexactly(HEADER_LENGTH)

                raw_payload_length = FrameDecoder.extract_payload_length(raw_header)

                raw_payload = await self.reader.readexactly(raw_payload_length)

                # self._incoming_frames.put_nowait(raw_header + raw_payload)
                self._protocol_session.handle_frame(raw_header + raw_payload)

        except asyncio.IncompleteReadError:
            logger.error("Can't read from client, client disconnected")
            raise

    async def _writer_loop(self):
        logger.info("Starting TCP Session writer loop, waiting to send messages")
        while True:
            frame = await self._outgoing_frames.get()
            try:
                self.writer.write(frame)
                await self.writer.drain()
            except Exception as e:
                logger.warning(f"Error writing to TCP client: {e}")
                raise

    async def _flush_writer_queue(self):
        logger.info("Flushing writer queue")
        while not self._outgoing_frames.empty():
            frame = await self._outgoing_frames.get()
            try:
                self.writer.write(frame)
                await asyncio.wait_for(self.writer.drain(), timeout=0.5)
            except Exception as e:
                logger.warning(f"Error sending frame during flush: {e}")
                break
        logger.info("Writer queue flushed")
