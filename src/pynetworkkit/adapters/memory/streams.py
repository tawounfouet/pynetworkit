"""Deterministic, bounded in-process duplex byte-stream adapter.

This models stream contract behavior, not TCP segmentation, network latency,
reliability, retransmission, or operating-system socket scheduling.
"""

from __future__ import annotations

import asyncio

from pynetworkkit.ports.streams import StreamClosedError


class _BytePipe:
    """One direction of byte flow, bounded by *bytes* (not queue entries)."""

    def __init__(self, max_buffer_bytes: int) -> None:
        self.max_buffer_bytes = max_buffer_bytes
        self._buffer = bytearray()
        self._writer_closed = False
        self._reader_closed = False
        self._changed = asyncio.Condition()

    async def read(self, max_bytes: int) -> bytes:
        async with self._changed:
            while not self._buffer and not self._writer_closed and not self._reader_closed:
                await self._changed.wait()
            if self._reader_closed:
                raise StreamClosedError("stream read side is closed")
            if not self._buffer:
                return b""
            size = min(max_bytes, len(self._buffer))
            chunk = bytes(self._buffer[:size])
            del self._buffer[:size]
            self._changed.notify_all()
            return chunk

    async def write(self, data: bytes) -> None:
        offset = 0
        async with self._changed:
            if self._writer_closed or self._reader_closed:
                raise StreamClosedError("stream write side is closed")
            while offset < len(data):
                while len(self._buffer) >= self.max_buffer_bytes:
                    if self._writer_closed or self._reader_closed:
                        raise StreamClosedError("stream closed during write")
                    await self._changed.wait()
                if self._writer_closed or self._reader_closed:
                    raise StreamClosedError("stream closed during write")
                size = min(self.max_buffer_bytes - len(self._buffer), len(data) - offset)
                self._buffer.extend(data[offset : offset + size])
                offset += size
                self._changed.notify_all()

    async def close_writer(self) -> None:
        async with self._changed:
            self._writer_closed = True
            self._changed.notify_all()

    async def close_reader(self) -> None:
        async with self._changed:
            self._reader_closed = True
            self._buffer.clear()
            self._changed.notify_all()


class MemoryByteStream:
    """An endpoint owning a read-side and a write-side of two byte pipes.

    A full close ends outgoing writes and closes local reads. It does not expose
    TCP half-close. Pending reads/writes wake on close; a cancelled write may
    leave an accepted prefix buffered. Simultaneous calls serialize per direction.
    """

    def __init__(self, incoming: _BytePipe, outgoing: _BytePipe) -> None:
        self._incoming = incoming
        self._outgoing = outgoing
        self._closed = False
        self._read_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()

    async def read(self, max_bytes: int) -> bytes:
        if type(max_bytes) is not int or max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")
        if self._closed:
            raise StreamClosedError("stream is closed")
        async with self._read_lock:
            if self._closed:
                raise StreamClosedError("stream is closed")
            return await self._incoming.read(max_bytes)

    async def write(self, data: bytes) -> None:
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        if self._closed:
            raise StreamClosedError("stream is closed")
        async with self._write_lock:
            if self._closed:
                raise StreamClosedError("stream is closed")
            await self._outgoing.write(data)

    async def aclose(self) -> None:
        # Repeat both shutdown steps on repeated calls, including recovery
        # from cancellation of a previous aclose attempt.
        self._closed = True
        await self._outgoing.close_writer()
        await self._incoming.close_reader()


def create_memory_stream_pair(
    *, max_buffer_bytes: int = 65536
) -> tuple[MemoryByteStream, MemoryByteStream]:
    """Create two connected endpoints with independently bounded byte buffers."""
    if type(max_buffer_bytes) is not int or max_buffer_bytes <= 0:
        raise ValueError("max_buffer_bytes must be a positive integer")
    a_to_b = _BytePipe(max_buffer_bytes)
    b_to_a = _BytePipe(max_buffer_bytes)
    return MemoryByteStream(b_to_a, a_to_b), MemoryByteStream(a_to_b, b_to_a)
