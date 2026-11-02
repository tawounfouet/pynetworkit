"""Synchronous UDP datagram capability contract and typed receive result.

An empty UDP datagram (b"") is valid data, never stream EOF. A received
datagram may be truncated: the excess was consumed and cannot be retrieved.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import TracebackType
from typing import Protocol, Self

from pynetworkkit.domain import IPEndpoint


@dataclass(frozen=True, slots=True)
class ReceivedDatagram:
    """One consumed UDP datagram with typed peer and truncation evidence.

    payload is a prefix of at most the requested max_bytes. When truncated
    is True, the remaining bytes were dropped by this receive operation.
    The original datagram size is not implied by these fields.
    """

    payload: bytes
    source: IPEndpoint
    truncated: bool

    def __post_init__(self) -> None:
        if not isinstance(self.payload, bytes):
            raise TypeError("Datagram payload must be bytes")
        if not isinstance(self.source, IPEndpoint):
            raise TypeError("Datagram source must be IPEndpoint")
        if type(self.truncated) is not bool:
            raise TypeError("Datagram truncated flag must be bool")


class SyncDatagramChannel(Protocol):
    """Own a blocking UDP socket; preserve per-datagram boundaries.

    send_to sends one complete datagram (including empty data), or raises;
    it never performs TCP-like partial-write retries or fragmentation.
    recv_from(max_bytes) permits max_bytes >= 0 and <= 65535 and returns an
    observable ReceivedDatagram. An implementation can read max_bytes + 1
    bytes to detect overflow cross-platform, then expose only max_bytes.
    UDP packets are consumed once even if truncated; there is no EOF marker.
    """

    @property
    def local_endpoint(self) -> IPEndpoint: ...

    def send_to(self, payload: bytes, destination: IPEndpoint) -> int: ...

    def recv_from(
        self, max_bytes: int, *, timeout: float | None = None
    ) -> ReceivedDatagram: ...

    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
