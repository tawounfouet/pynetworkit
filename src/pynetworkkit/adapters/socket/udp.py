"""Blocking UDP datagram channel; source and truncation are always observable."""
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
)
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import ReceivedDatagram, StreamClosedError


class SocketUDPChannel:
    """Own one bound UDP socket, optionally accepting zero-length datagrams."""

    def __init__(self, sock: socket.socket) -> None:
        self._socket = sock
        self._closed = False

    @classmethod
    def bind(cls, local: IPEndpoint) -> SocketUDPChannel:
        family = address_family(local)
        sock = socket.socket(family, socket.SOCK_DGRAM)
        try:
            enable_ipv6_only(sock, family)
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

    def send_to(
        self, payload: bytes, destination: IPEndpoint, *, timeout: float | None = None
    ) -> int:
        if not isinstance(payload, bytes):
            raise TypeError("payload must be bytes")
        target_family = address_family(destination)
        self._check_open()
        if target_family != self._socket.family:
            raise ValueError("UDP destination IP family differs from channel")
        with temporary_timeout(self._socket, timeout):
            sent = self._socket.sendto(payload, socket_address(destination))
        if sent != len(payload):
            raise OSError("UDP send did not accept the entire datagram")
        return sent

    def recv_from(
        self, max_bytes: int, *, timeout: float | None = None
    ) -> ReceivedDatagram:
        if type(max_bytes) is not int or not 0 <= max_bytes <= 65535:
            raise ValueError("max_bytes must be an integer in 0..65535")
        self._check_open()
        # One byte beyond the caller's bound detects silent UDP truncation on
        # POSIX and Windows without depending on recvmsg/MSG_TRUNC.
        with temporary_timeout(self._socket, timeout):
            raw, addr = self._socket.recvfrom(max_bytes + 1)
        return ReceivedDatagram(
            payload=raw[:max_bytes],
            source=endpoint_from_sockaddr(addr),
            truncated=len(raw) > max_bytes,
        )

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
