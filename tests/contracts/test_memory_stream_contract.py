"""Reusable stream behavioral contract exercised with memory adapter."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio

from pynetworkkit.adapters.memory import MemoryByteStream, create_memory_stream_pair
from pynetworkkit.ports import AsyncByteStream, StreamClosedError
from tests.contracts.stream_contracts import (
    assert_closed_writer,
    assert_eof_after_drain,
    assert_stream_roundtrip,
)


@pytest_asyncio.fixture
async def stream_pair() -> AsyncIterator[tuple[AsyncByteStream, AsyncByteStream]]:
    left, right = create_memory_stream_pair()
    try:
        yield left, right
    finally:
        await left.aclose()
        await right.aclose()


@pytest.mark.asyncio
async def test_roundtrip(stream_pair: tuple[AsyncByteStream, AsyncByteStream]) -> None:
    await assert_stream_roundtrip(*stream_pair)


@pytest.mark.asyncio
async def test_eof_after_drain(stream_pair: tuple[AsyncByteStream, AsyncByteStream]) -> None:
    await assert_eof_after_drain(*stream_pair)


@pytest.mark.asyncio
async def test_closed_operations(stream_pair: tuple[AsyncByteStream, AsyncByteStream]) -> None:
    await assert_closed_writer(stream_pair[0])


@pytest.mark.asyncio
async def test_empty_write_is_noop(stream_pair: tuple[AsyncByteStream, AsyncByteStream]) -> None:
    left, right = stream_pair
    await left.write(b"")
    await left.write(b"x")
    assert await right.read(4) == b"x"


@pytest.mark.asyncio
async def test_read_argument_validation(
    stream_pair: tuple[AsyncByteStream, AsyncByteStream],
) -> None:
    for value in (0, -1, True):
        with pytest.raises(ValueError):
            await stream_pair[0].read(value)


@pytest.mark.asyncio
async def test_peer_close_wakes_pending_read(
    stream_pair: tuple[AsyncByteStream, AsyncByteStream],
) -> None:
    left, right = stream_pair
    task = asyncio.create_task(right.read(1))
    await asyncio.sleep(0)
    await left.aclose()
    assert await asyncio.wait_for(task, timeout=2) == b""


@pytest.mark.asyncio
async def test_bounded_backpressure_waits_for_consumption() -> None:
    left, right = create_memory_stream_pair(max_buffer_bytes=2)
    try:
        task = asyncio.create_task(left.write(b"abcd"))
        await asyncio.sleep(0)
        assert not task.done()
        assert await asyncio.wait_for(right.read(2), timeout=2) == b"ab"
        await asyncio.wait_for(task, timeout=2)
        assert await right.read(4) == b"cd"
    finally:
        await left.aclose()
        await right.aclose()


@pytest.mark.asyncio
async def test_cancel_blocked_writer_and_cleanup() -> None:
    left, right = create_memory_stream_pair(max_buffer_bytes=1)
    try:
        await left.write(b"a")
        task = asyncio.create_task(left.write(b"b"))
        await asyncio.sleep(0)
        assert not task.done()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert await right.read(1) == b"a"
        await left.write(b"c")
        assert await right.read(1) == b"c"
    finally:
        await left.aclose()
        await right.aclose()


@pytest.mark.asyncio
async def test_cancel_blocked_reader_then_continue() -> None:
    left, right = create_memory_stream_pair()
    try:
        pending = asyncio.create_task(right.read(1))
        await asyncio.sleep(0)
        pending.cancel()
        with pytest.raises(asyncio.CancelledError):
            await pending
        await left.write(b"x")
        assert await asyncio.wait_for(right.read(1), timeout=2) == b"x"
    finally:
        await left.aclose()
        await right.aclose()


@pytest.mark.asyncio
async def test_close_wakes_blocked_writer() -> None:
    left, right = create_memory_stream_pair(max_buffer_bytes=1)
    try:
        await left.write(b"x")
        task = asyncio.create_task(left.write(b"y"))
        await asyncio.sleep(0)
        await right.aclose()
        with pytest.raises(StreamClosedError):
            await asyncio.wait_for(task, timeout=2)
    finally:
        await left.aclose()
        await right.aclose()


@pytest.mark.asyncio
async def test_close_is_idempotent() -> None:
    left, right = create_memory_stream_pair()
    await left.aclose()
    await left.aclose()
    await right.aclose()
    await right.aclose()


@pytest.mark.asyncio
async def test_peer_close_fails_future_write() -> None:
    left, right = create_memory_stream_pair()
    try:
        await right.aclose()
        with pytest.raises(StreamClosedError):
            await left.write(b"payload")
    finally:
        await left.aclose()


@pytest.mark.asyncio
async def test_reject_nonbytes_write() -> None:
    left, right = create_memory_stream_pair()
    try:
        with pytest.raises(TypeError):
            await left.write("not bytes")  # type: ignore[arg-type]
    finally:
        await left.aclose()
        await right.aclose()


@pytest.mark.parametrize("capacity", [0, -1, True, 1.5, "5"])
def test_invalid_capacity(capacity: object) -> None:
    with pytest.raises(ValueError):
        create_memory_stream_pair(max_buffer_bytes=capacity)  # type: ignore[arg-type]


def test_runtime_protocol_conformity() -> None:
    left, right = create_memory_stream_pair()
    assert isinstance(left, MemoryByteStream)
    assert isinstance(right, MemoryByteStream)
