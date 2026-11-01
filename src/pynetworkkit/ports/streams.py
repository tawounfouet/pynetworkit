"""Minimal asynchronous stream and connector capability contracts.

A stream is ordered bytes, not an application-message transport. Interfaces
make no assumptions about a particular event loop or OS network stack.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pynetworkkit.domain import IPEndpoint


class StreamClosedError(RuntimeError):
    """Operation is not allowed after local or remote stream shutdown."""


class AsyncByteStream(Protocol):
    """Single-reader/single-writer stream; lifecycle ownership is explicit.

    read(n) requires n > 0 and returns at most n bytes; b'' means remote EOF.
    write(bytes) returns after all bytes are accepted into the transport, not
    necessarily received by the peer. A cancelled write may be partly accepted.
    aclose() is idempotent; closing locally invalidates local reads/writes.
    """

    async def read(self, max_bytes: int) -> bytes: ...

    async def write(self, data: bytes) -> None: ...

    async def aclose(self) -> None: ...


class AsyncStreamConnector(Protocol):
    """Open a byte stream to a validated IP endpoint."""

    async def connect(self, endpoint: IPEndpoint) -> AsyncByteStream: ...
