"""Non-blocking TCP asyncio adapters with explicit socket ownership."""

from __future__ import annotations

import asyncio
import socket
from types import TracebackType
from typing import Self

from pynetworkkit.adapters.socket._common import (
    address_family,
    enable_ipv6_only,
    endpoint_from_sockaddr,
    socket_address,
)
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import StreamClosedError

_WRITE_CHUNK_BYTES = 16384


class AsyncioTCPStream:
    """One reader and one writer; writers drain in bounded chunks.

    A successful write does not mean the peer received the bytes. Cancellation
    may have accepted a prefix, and the caller must not blindly retry.
    """

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        self._reader = reader
        self._writer = writer
        self._closed = False
        self._read_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()

    def _check_open(self) -> None:
        if self._closed:
            raise StreamClosedError("TCP stream is closed")

    @property
    def local_endpoint(self) -> IPEndpoint:
        self._check_open()
        return endpoint_from_sockaddr(self._writer.get_extra_info("sockname"))

    @property
    def remote_endpoint(self) -> IPEndpoint:
        self._check_open()
        return endpoint_from_sockaddr(self._writer.get_extra_info("peername"))

    async def read(self, max_bytes: int) -> bytes:
        if type(max_bytes) is not int or max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")
        self._check_open()
        async with self._read_lock:
            self._check_open()
            result = await self._reader.read(max_bytes)
            self._check_open()
            return result

    async def write(self, data: bytes) -> None:
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        self._check_open()
        async with self._write_lock:
            self._check_open()
            # Drain after each bounded chunk instead of enqueueing a huge
            # caller-provided payload in the event-loop transport all at once.
            for start in range(0, len(data), _WRITE_CHUNK_BYTES):
                self._check_open()
                self._writer.write(data[start : start + _WRITE_CHUNK_BYTES])
                await self._writer.drain()
                self._check_open()

    async def aclose(self) -> None:
        self._closed = True
        self._writer.close()
        # Repeated close can recover if the previous wait was cancelled.
        await self._writer.wait_closed()

    async def __aenter__(self) -> Self:
        self._check_open()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()


class AsyncioTCPConnector:
    """Open a TCP connection to an already resolved IP endpoint."""

    async def connect(self, endpoint: IPEndpoint) -> AsyncioTCPStream:
        if not isinstance(endpoint, IPEndpoint):
            raise TypeError("endpoint must be IPEndpoint")
        if endpoint.port.value == 0:
            raise ValueError("TCP destination port must not be zero")
        reader, writer = await asyncio.open_connection(
            host=str(endpoint.address), port=endpoint.port.value
        )
        return AsyncioTCPStream(reader, writer)


class AsyncioTCPListener:
    """Pull-based async accept loop; owns only the listening socket."""

    def __init__(self, sock: socket.socket) -> None:
        self._socket = sock
        self._closed = False
        self._accept_lock = asyncio.Lock()
        self._accepting_tasks: set[asyncio.Task[object]] = set()

    @classmethod
    def bind(cls, local: IPEndpoint, *, backlog: int = 128) -> AsyncioTCPListener:
        if type(backlog) is not int or backlog <= 0:
            raise ValueError("backlog must be a positive integer")
        family = address_family(local)
        sock = socket.socket(family, socket.SOCK_STREAM)
        try:
            enable_ipv6_only(sock, family)
            sock.setblocking(False)
            sock.bind(socket_address(local))
            sock.listen(backlog)
            return cls(sock)
        except BaseException:
            sock.close()
            raise

    def _check_open(self) -> None:
        if self._closed:
            raise StreamClosedError("TCP listener is closed")

    @property
    def local_endpoint(self) -> IPEndpoint:
        self._check_open()
        return endpoint_from_sockaddr(self._socket.getsockname())

    async def accept(self) -> tuple[AsyncioTCPStream, IPEndpoint]:
        self._check_open()
        task = asyncio.current_task()
        if task is not None:
            self._accepting_tasks.add(task)
        try:
            async with self._accept_lock:
                self._check_open()
                accepted, peer = await asyncio.get_running_loop().sock_accept(self._socket)
                try:
                    self._check_open()
                    accepted.setblocking(False)
                    reader, writer = await asyncio.open_connection(sock=accepted)
                    # asyncio owns the accepted socket after open_connection.
                    return AsyncioTCPStream(reader, writer), endpoint_from_sockaddr(peer)
                except BaseException:
                    accepted.close()
                    raise
        finally:
            if task is not None:
                self._accepting_tasks.discard(task)

    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True
            self._socket.close()
            current = asyncio.current_task()
            for task in tuple(self._accepting_tasks):
                if task is not current:
                    task.cancel()

    async def __aenter__(self) -> Self:
        self._check_open()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()
