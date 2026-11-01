"""Shared behavioral assertions for future stream implementations (M1/M2)."""

from __future__ import annotations

import asyncio

import pytest

from pynetworkkit.ports import AsyncByteStream, StreamClosedError


async def assert_stream_roundtrip(left: AsyncByteStream, right: AsyncByteStream) -> None:
    await asyncio.wait_for(left.write(b"abcdef"), timeout=2)
    assert await asyncio.wait_for(right.read(2), timeout=2) == b"ab"
    assert await asyncio.wait_for(right.read(4), timeout=2) == b"cdef"
    await asyncio.wait_for(right.write(b"reply"), timeout=2)
    assert await asyncio.wait_for(left.read(5), timeout=2) == b"reply"


async def assert_eof_after_drain(left: AsyncByteStream, right: AsyncByteStream) -> None:
    await left.write(b"hello")
    await left.aclose()
    assert await asyncio.wait_for(right.read(3), timeout=2) == b"hel"
    assert await asyncio.wait_for(right.read(3), timeout=2) == b"lo"
    assert await asyncio.wait_for(right.read(3), timeout=2) == b""
    assert await asyncio.wait_for(right.read(3), timeout=2) == b""


async def assert_closed_writer(left: AsyncByteStream) -> None:
    await left.aclose()
    await left.aclose()
    with pytest.raises(StreamClosedError):
        await left.write(b"unexpected")
    with pytest.raises(StreamClosedError):
        await left.read(1)
