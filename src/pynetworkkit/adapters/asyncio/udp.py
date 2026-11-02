"""Native UDP datagram adapter using nonblocking asyncio socket operations."""

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
from pynetworkkit.ports import ReceivedDatagram, StreamClosedError


class AsyncioUDPChannel:
    """UDP peer identity and truncation semantics identical to M1.

    Exactly one reader at a time. A full 65535-byte receive buffer avoids
    Windows' short-buffer WSAEMSGSIZE path. No UDP EOF exists.
    """

    def __init__(self, sock: socket.socket) -> None:
        self._socket = sock
        self._closed = False
        self._receive_lock = asyncio.Lock()
        self._send_lock = asyncio.Lock()
        self._receive_tasks: set[asyncio.Task[object]] = set()

    @classmethod
    def bind(cls, local: IPEndpoint) -> AsyncioUDPChannel:
        family = address_family(local)
        sock = socket.socket(family, socket.SOCK_DGRAM)
        try:
            enable_ipv6_only(sock, family)
            sock.setblocking(False)
            sock.bind(socket_address(local))
            return cls(sock)
        except BaseException:
            sock.close()
            raise

    def _check_open(self) -> None:
        if self._closed:
            raise StreamClosedError("UDP channel is closed")

    @property
    def local_endpoint(self) -> IPEndpoint:
        self._check_open()
        return endpoint_from_sockaddr(self._socket.getsockname())

    async def send_to(self, payload: bytes, destination: IPEndpoint) -> int:
        if not isinstance(payload, bytes):
            raise TypeError("payload must be bytes")
        family = address_family(destination)
        self._check_open()
        if family != self._socket.family:
            raise ValueError("UDP destination family differs from bound socket")
        if destination.port.value == 0:
            raise ValueError("UDP destination port must not be zero")
        async with self._send_lock:
            self._check_open()
            count = await asyncio.get_running_loop().sock_sendto(
                self._socket, payload, socket_address(destination)
            )
            if count != len(payload):
                raise OSError("UDP send did not accept the entire datagram")
            return count

    async def recv_from(self, max_bytes: int) -> ReceivedDatagram:
        if type(max_bytes) is not int or not 0 <= max_bytes <= 65535:
            raise ValueError("max_bytes must be an integer in 0..65535")
        self._check_open()
        task = asyncio.current_task()
        if task is not None:
            self._receive_tasks.add(task)
        try:
            async with self._receive_lock:
                self._check_open()
                raw, peer = await asyncio.get_running_loop().sock_recvfrom(self._socket, 65535)
                self._check_open()
                return ReceivedDatagram(
                    payload=raw[:max_bytes],
                    source=endpoint_from_sockaddr(peer),
                    truncated=len(raw) > max_bytes,
                )
        finally:
            if task is not None:
                self._receive_tasks.discard(task)

    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True
            self._socket.close()
            current = asyncio.current_task()
            for task in tuple(self._receive_tasks):
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
