"""Deterministic M2 cancellation injection for connect/write/close.

These tests use explicit events, not wall-clock scheduling assumptions.
"""

import asyncio
from typing import cast

import pytest

from pynetworkkit.adapters.asyncio import AsyncioTCPConnector, AsyncioTCPStream
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import StreamClosedError


@pytest.mark.asyncio
async def test_cancel_pending_tcp_connect_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    started = asyncio.Event()

    async def stalled_connect(*args: object, **kwargs: object) -> None:
        started.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(asyncio, "open_connection", stalled_connect)
    task = asyncio.create_task(AsyncioTCPConnector().connect(IPEndpoint.parse("127.0.0.1", 10001)))
    await asyncio.wait_for(started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(task, 2)
    assert task.done()


class _ControlledWriter:
    """Minimal deterministic StreamWriter substitute with explicit checkpoints."""

    def __init__(self) -> None:
        self.accepted: list[bytes] = []
        self.drain_started = asyncio.Event()
        self.allow_drain = asyncio.Event()
        self.close_started = asyncio.Event()
        self.allow_close = asyncio.Event()
        self.closed = False

    def write(self, data: bytes) -> None:
        self.accepted.append(data)

    async def drain(self) -> None:
        self.drain_started.set()
        await self.allow_drain.wait()

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        self.close_started.set()
        await self.allow_close.wait()


@pytest.mark.asyncio
async def test_cancel_partial_write_then_recover_cancelled_close() -> None:
    writer = _ControlledWriter()
    stream = AsyncioTCPStream(
        asyncio.StreamReader(),
        cast(asyncio.StreamWriter, writer),
    )
    task = asyncio.create_task(stream.write(b"q" * 17000))
    await asyncio.wait_for(writer.drain_started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(task, 2)
    assert len(writer.accepted) == 1
    assert len(writer.accepted[0]) == 16384

    writer.allow_drain.set()
    closing = asyncio.create_task(stream.aclose())
    await asyncio.wait_for(writer.close_started.wait(), 2)
    closing.cancel()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(closing, 2)

    writer.allow_close.set()
    await asyncio.wait_for(stream.aclose(), 2)
    assert writer.closed
    with pytest.raises(StreamClosedError):
        await stream.write(b"after-close")


def test_half_close_deliberately_not_part_of_m2_port() -> None:
    assert not hasattr(AsyncioTCPStream, "shutdown_write")
