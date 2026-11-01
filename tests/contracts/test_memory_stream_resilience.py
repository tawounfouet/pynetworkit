"""Bounded async cancellation, timeout and cleanup qualification for M0 E3."""

from __future__ import annotations

import asyncio

import pytest

from pynetworkkit.adapters.memory import create_memory_stream_pair
from pynetworkkit.ports import StreamClosedError


@pytest.mark.asyncio
async def test_read_deadline_expires_without_consuming_future_bytes() -> None:
    left, right = create_memory_stream_pair(max_buffer_bytes=2)
    try:
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(right.read(1), timeout=0.03)
        await left.write(b"x")
        assert await asyncio.wait_for(right.read(1), timeout=1) == b"x"
    finally:
        await left.aclose()
        await right.aclose()


@pytest.mark.asyncio
async def test_write_deadline_preserves_preexisting_bytes() -> None:
    left, right = create_memory_stream_pair(max_buffer_bytes=1)
    try:
        await left.write(b"a")
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(left.write(b"b"), timeout=0.03)
        assert await right.read(1) == b"a"
        await left.write(b"c")
        assert await right.read(1) == b"c"
    finally:
        await left.aclose()
        await right.aclose()


@pytest.mark.asyncio
async def test_cancelled_partial_write_retains_accepted_prefix() -> None:
    left, right = create_memory_stream_pair(max_buffer_bytes=1)
    writer = asyncio.create_task(left.write(b"abc"))
    try:
        await asyncio.sleep(0)
        assert not writer.done()
        writer.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(writer, timeout=1)
        assert await right.read(1) == b"a"
        await left.aclose()
        assert await right.read(1) == b""
    finally:
        if not writer.done():
            writer.cancel()
            await asyncio.gather(writer, return_exceptions=True)
        await left.aclose()
        await right.aclose()
    assert writer.done()


@pytest.mark.asyncio
async def test_local_close_releases_its_blocked_reader() -> None:
    left, right = create_memory_stream_pair()
    reader = asyncio.create_task(left.read(1))
    try:
        await asyncio.sleep(0)
        assert not reader.done()
        await left.aclose()
        with pytest.raises(StreamClosedError):
            await asyncio.wait_for(reader, timeout=1)
    finally:
        if not reader.done():
            reader.cancel()
            await asyncio.gather(reader, return_exceptions=True)
        await left.aclose()
        await right.aclose()
    assert reader.done()


@pytest.mark.asyncio
async def test_multiple_waiting_readers_can_be_cancelled_without_orphans() -> None:
    left, right = create_memory_stream_pair()
    readers = [asyncio.create_task(right.read(1)) for _ in range(6)]
    try:
        await asyncio.sleep(0)
        for reader in readers:
            reader.cancel()
        results = await asyncio.wait_for(
            asyncio.gather(*readers, return_exceptions=True), timeout=1
        )
        assert all(isinstance(result, asyncio.CancelledError) for result in results)
        await left.write(b"x")
        assert await asyncio.wait_for(right.read(1), timeout=1) == b"x"
    finally:
        for reader in readers:
            if not reader.done():
                reader.cancel()
        await asyncio.gather(*readers, return_exceptions=True)
        await left.aclose()
        await right.aclose()
    assert all(reader.done() for reader in readers)


@pytest.mark.asyncio
async def test_duplex_directions_have_independent_byte_limits() -> None:
    left, right = create_memory_stream_pair(max_buffer_bytes=1)
    try:
        await left.write(b"a")
        await right.write(b"b")
        assert await left.read(1) == b"b"
        assert await right.read(1) == b"a"
    finally:
        await left.aclose()
        await right.aclose()


@pytest.mark.asyncio
async def test_long_payload_is_lossless_under_slow_consumer() -> None:
    left, right = create_memory_stream_pair(max_buffer_bytes=3)
    payload = bytes(range(100))
    writer = asyncio.create_task(left.write(payload))
    received = bytearray()
    try:
        while len(received) < len(payload):
            received.extend(await asyncio.wait_for(right.read(7), timeout=1))
        await asyncio.wait_for(writer, timeout=1)
        assert bytes(received) == payload
    finally:
        if not writer.done():
            writer.cancel()
        await asyncio.gather(writer, return_exceptions=True)
        await left.aclose()
        await right.aclose()
    assert writer.done()


@pytest.mark.asyncio
async def test_serialized_writers_do_not_interleave_bytes() -> None:
    left, right = create_memory_stream_pair(max_buffer_bytes=2)
    first = asyncio.create_task(left.write(b"abc"))
    second = asyncio.create_task(left.write(b"XYZ"))
    data = bytearray()
    try:
        while len(data) < 6:
            data.extend(await asyncio.wait_for(right.read(2), timeout=1))
        await asyncio.wait_for(asyncio.gather(first, second), timeout=1)
        assert bytes(data) == b"abcXYZ"
    finally:
        for task in (first, second):
            if not task.done():
                task.cancel()
        await asyncio.gather(first, second, return_exceptions=True)
        await left.aclose()
        await right.aclose()
    assert first.done() and second.done()
