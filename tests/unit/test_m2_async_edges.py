"""M2 negative and lifecycle cases close gaps in portability coverage."""

import asyncio

import pytest

from pynetworkkit.adapters.asyncio import (
    AsyncioTCPConnector,
    AsyncioTCPListener,
    AsyncioUDPChannel,
)
from pynetworkkit.application.bounded import BoundedByteQueue, bounded_map
from pynetworkkit.application.deadlines import Deadline
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import StreamClosedError


@pytest.mark.asyncio
async def test_tcp_context_ownership_and_endpoint_properties() -> None:
    listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
    async with listener:
        client = await AsyncioTCPConnector().connect(listener.local_endpoint)
        server, peer = await listener.accept()
        assert peer.address.is_loopback
        async with client, server:
            assert client.local_endpoint == server.remote_endpoint
            assert client.remote_endpoint == server.local_endpoint
            with pytest.raises(ValueError):
                await client.read(True)
            with pytest.raises(TypeError):
                await client.write("bad")  # type: ignore[arg-type]
    with pytest.raises(StreamClosedError):
        _ = listener.local_endpoint


@pytest.mark.asyncio
async def test_tcp_invalid_endpoint_and_listener_options() -> None:
    with pytest.raises(ValueError):
        AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0), backlog=0)
    with pytest.raises(ValueError):
        await AsyncioTCPConnector().connect(IPEndpoint.parse("127.0.0.1", 0))
    listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
    await listener.aclose()
    with pytest.raises(StreamClosedError):
        await listener.accept()


@pytest.mark.asyncio
async def test_udp_context_manager_and_empty_payload() -> None:
    a = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    b = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    try:
        async with a, b:
            async with asyncio.timeout(3):
                assert await a.send_to(b"", b.local_endpoint) == 0
                datagram = await b.recv_from(0)
                assert datagram.payload == b"" and not datagram.truncated
    finally:
        await a.aclose()
        await b.aclose()
    with pytest.raises(StreamClosedError):
        _ = b.local_endpoint


@pytest.mark.asyncio
async def test_queue_close_wakes_empty_waiter_and_enforces_item_limit() -> None:
    queue = BoundedByteQueue(max_bytes=10, max_items=1)
    waiting = asyncio.create_task(queue.get())
    await asyncio.sleep(0)
    await queue.aclose()
    with pytest.raises(StreamClosedError):
        await asyncio.wait_for(waiting, 2)

    queue2 = BoundedByteQueue(max_bytes=10, max_items=1)
    with pytest.raises(TypeError):
        await queue2.put("wrong")  # type: ignore[arg-type]
    await queue2.put(b"")
    waiting_put = asyncio.create_task(queue2.put(b""))
    await asyncio.sleep(0)
    assert not waiting_put.done()
    assert queue2.qsize == 1
    assert await queue2.get() == b""
    await asyncio.wait_for(waiting_put, 2)
    assert await queue2.get() == b""
    await queue2.aclose()


@pytest.mark.asyncio
async def test_bounded_map_empty_errors_and_limits() -> None:
    async def worker(item: int) -> int:
        if item == 2:
            raise RuntimeError("expected worker error")
        await asyncio.sleep(0)
        return item

    assert await bounded_map([], worker, max_tasks=2) == []
    with pytest.raises(ValueError):
        await bounded_map([1], worker, max_tasks=0)
    with pytest.raises(ExceptionGroup):
        await bounded_map([1, 2, 3], worker, max_tasks=2)


def test_deadline_absolute_validation_and_exhaustion() -> None:
    with pytest.raises(ValueError):
        Deadline(float("nan"))
    with pytest.raises(ValueError):
        Deadline(float("inf"))
    with pytest.raises(TypeError):
        Deadline(True)
    deadline = Deadline(12.0)
    assert deadline.remaining(clock=lambda: 13.0) == 0.0
