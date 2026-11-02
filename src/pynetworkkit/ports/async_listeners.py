"""Pull-based async TCP listener contract independent of asyncio.

The listener exclusively owns its passive socket. An accepted connected socket
is transferred to the returned stream; closing the listener does not close it.
"""

from __future__ import annotations

from typing import Protocol

from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports.streams import AsyncByteStream


class AsyncStreamListener(Protocol):
    """Accept one client at a time; never block the event loop."""

    @property
    def local_endpoint(self) -> IPEndpoint: ...

    async def accept(self) -> tuple[AsyncByteStream, IPEndpoint]: ...

    async def aclose(self) -> None: ...
