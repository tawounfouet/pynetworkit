"""Synchronous TCP byte-stream capability contracts (M1/E00).

Ports declare behavior, not operating-system socket implementations. Unlike the
M0 AsyncByteStream, write() is a single partial-write operation returning an
integer. These protocols do not import socket or asyncio.
"""

from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self

from pynetworkkit.domain import IPEndpoint


class SyncByteStream(Protocol):
    """Owned, blocking TCP byte stream.

    read(max_bytes, timeout=None): requires positive int; returns at most max_bytes bytes.
    b"" signals peer EOF only. TCP has no application message boundaries.
    write(data, timeout=None): requires bytes; returns 0 < n <= len(data) for nonempty data,
    and 0 for empty bytes. The caller handles partial writes. A zero-byte
    send of nonempty data must raise, never loop indefinitely.
    shutdown_write(): half-closes the local write direction while keeping reads.
    close(): idempotently releases the owned handle. Post-close I/O raises.
    """

    @property
    def local_endpoint(self) -> IPEndpoint: ...

    @property
    def remote_endpoint(self) -> IPEndpoint: ...

    def read(self, max_bytes: int, *, timeout: float | None = None) -> bytes: ...

    def write(self, data: bytes, *, timeout: float | None = None) -> int: ...

    def shutdown_write(self) -> None: ...

    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...


class SyncStreamConnector(Protocol):
    """Create a connected, exclusively owned stream for a numeric IP endpoint."""

    def connect(self, remote: IPEndpoint, *, timeout: float | None = None) -> SyncByteStream: ...


class SyncStreamListener(Protocol):
    """Own a listening socket and transfer each accepted socket to a stream.

    The listener continues owning only its listening socket. Closing the
    listener does not implicitly close already accepted streams.
    """

    @property
    def local_endpoint(self) -> IPEndpoint: ...

    def accept(self, *, timeout: float | None = None) -> tuple[SyncByteStream, IPEndpoint]: ...

    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
