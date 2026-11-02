"""Bounded queues must hold resource invariants under backpressure."""

import asyncio

import pytest

from pynetworkkit.application.bounded import BoundedByteQueue, bounded_map
from pynetworkkit.ports import StreamClosedError


@pytest.mark.asyncio
async def test_slow_consumer_propagates_backpressure() -> None:
    queue = BoundedByteQueue(max_bytes=3, max_items=2)
    await queue.put(b"ab")
    producer = asyncio.create_task(queue.put(b"cd"))
    await asyncio.sleep(0)
    assert not producer.done()
    assert queue.buffered_bytes == 2
    assert await queue.get() == b"ab"
    await asyncio.wait_for(producer, 2)
    assert queue.buffered_bytes == 2
    assert queue.qsize == 1
    assert await queue.get() == b"cd"
    await queue.aclose()


@pytest.mark.asyncio
async def test_close_releases_waiting_producer_and_consumer() -> None:
    queue = BoundedByteQueue(max_bytes=1, max_items=1)
    await queue.put(b"x")
    waiting = asyncio.create_task(queue.put(b"y"))
    await asyncio.sleep(0)
    await queue.aclose()
    with pytest.raises(StreamClosedError):
        await asyncio.wait_for(waiting, 2)
    assert await queue.get() == b"x"
    with pytest.raises(StreamClosedError):
        await queue.get()


@pytest.mark.asyncio
async def test_cancelled_producer_does_not_reserve_byte_credits() -> None:
    queue = BoundedByteQueue(max_bytes=1, max_items=1)
    await queue.put(b"a")
    waiting = asyncio.create_task(queue.put(b"b"))
    await asyncio.sleep(0)
    waiting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiting
    assert queue.buffered_bytes == 1
    assert await queue.get() == b"a"
    await queue.put(b"c")
    assert await queue.get() == b"c"
    await queue.aclose()


@pytest.mark.asyncio
async def test_bounded_map_preserves_order_and_caps_tasks() -> None:
    active = 0
    peak = 0

    async def operation(item: int) -> int:
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0)
        active -= 1
        return item * 2

    values = await bounded_map(list(range(40)), operation, max_tasks=3)
    assert values == list(range(0, 80, 2))
    assert 1 <= peak <= 3
    assert active == 0


def test_limits_are_strict() -> None:
    with pytest.raises(ValueError):
        BoundedByteQueue(max_bytes=0, max_items=1)
    with pytest.raises(ValueError):
        BoundedByteQueue(max_bytes=1, max_items=True)


@pytest.mark.asyncio
async def test_oversized_payload_rejected() -> None:
    queue = BoundedByteQueue(max_bytes=2, max_items=1)
    with pytest.raises(ValueError):
        await queue.put(b"xyz")
    await queue.aclose()
