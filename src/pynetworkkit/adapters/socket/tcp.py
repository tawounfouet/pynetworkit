"""Blocking TCP socket adapters with explicit exclusive resource ownership."""

from __future__ import annotations

import socket
from types import TracebackType
from typing import Self

from pynetworkkit.adapters.socket._common import (
    address_family,
    enable_ipv6_only,
    endpoint_from_sockaddr,
    socket_address,
    temporary_timeout,
    validate_timeout,
)
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import StreamClosedError


class SocketTCPStream:
    """Own an already connected TCP socket; close transfers no ownership back."""

    def __init__(self, sock: socket.socket) -> None:
        self._socket = sock
        self._closed = False
        self._write_shutdown = False

    @property
    def local_endpoint(self) -> IPEndpoint:
        self._check_open()
        return endpoint_from_sockaddr(self._socket.getsockname())

    @property
    def remote_endpoint(self) -> IPEndpoint:
        self._check_open()
        return endpoint_from_sockaddr(self._socket.getpeername())

    def _check_open(self) -> None:
        if self._closed:
            raise StreamClosedError("TCP stream is closed")

    def read(self, max_bytes: int, *, timeout: float | None = None) -> bytes:
        if type(max_bytes) is not int or max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")
        self._check_open()
        with temporary_timeout(self._socket, timeout):
            return self._socket.recv(max_bytes)

    def write(self, data: bytes, *, timeout: float | None = None) -> int:
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        self._check_open()
        if self._write_shutdown:
            raise StreamClosedError("TCP write direction was shut down")
        if not data:
            return 0
        with temporary_timeout(self._socket, timeout):
            written = self._socket.send(data)
        if not 0 < written <= len(data):
            raise ConnectionError("TCP send made no valid progress")
        return written

    def shutdown_write(self) -> None:
        self._check_open()
        if self._write_shutdown:
            return
        self._socket.shutdown(socket.SHUT_WR)
        self._write_shutdown = True

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._socket.close()

    def __enter__(self) -> Self:
        self._check_open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


class SocketTCPConnector:
    """Factory of exclusively owned connected TCP streams."""

    def connect(self, remote: IPEndpoint, *, timeout: float | None = None) -> SocketTCPStream:
        family = address_family(remote)
        if remote.port.value == 0:
            raise ValueError("TCP destination port must not be zero")
        timeout = validate_timeout(timeout)
        sock = socket.socket(family, socket.SOCK_STREAM)
        try:
            enable_ipv6_only(sock, family)
            with temporary_timeout(sock, timeout):
                sock.connect(socket_address(remote))
            return SocketTCPStream(sock)
        except BaseException:
            sock.close()
            raise


class SocketTCPListener:
    """Own a listening socket and transfer accepted sockets into streams."""

    def __init__(self, sock: socket.socket) -> None:
        self._socket = sock
        self._closed = False

    @classmethod
    def bind(cls, local: IPEndpoint, *, backlog: int = 128) -> SocketTCPListener:
        family = address_family(local)
        if type(backlog) is not int or backlog <= 0:
            raise ValueError("backlog must be a positive integer")
        sock = socket.socket(family, socket.SOCK_STREAM)
        try:
            enable_ipv6_only(sock, family)
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

    def accept(self, *, timeout: float | None = None) -> tuple[SocketTCPStream, IPEndpoint]:
        self._check_open()
        with temporary_timeout(self._socket, timeout):
            accepted, raw_address = self._socket.accept()
        try:
            remote = endpoint_from_sockaddr(raw_address)
            return SocketTCPStream(accepted), remote
        except BaseException:
            accepted.close()
            raise

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._socket.close()

    def __enter__(self) -> Self:
        self._check_open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
