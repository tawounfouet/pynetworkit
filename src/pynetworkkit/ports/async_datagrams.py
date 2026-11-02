"""Async UDP contract matching M1's ReceivedDatagram semantics."""
from __future__ import annotations

from typing import Protocol

from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports.sync_datagrams import ReceivedDatagram


class AsyncDatagramChannel(Protocol):
    """Own a UDP socket and preserve message boundaries.

    A successful send_to returns the entire datagram length, including zero.
    recv_from consumes exactly one datagram and reports truncation. Empty
    datagrams are legitimate payloads, not EOF. No delivery guarantee exists.
    """

    @property
    def local_endpoint(self) -> IPEndpoint: ...

    async def send_to(self, payload: bytes, destination: IPEndpoint) -> int: ...

    async def recv_from(self, max_bytes: int) -> ReceivedDatagram: ...

    async def aclose(self) -> None: ...
