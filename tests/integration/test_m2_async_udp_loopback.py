"""UDP M2 loopback contract including empty and truncated datagrams."""

import asyncio

import pytest

from pynetworkkit.adapters.asyncio import AsyncioUDPChannel
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import StreamClosedError


@pytest.mark.asyncio
async def test_udp_roundtrip_peer_empty_and_truncation() -> None:
    left = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    right = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    try:
        async with asyncio.timeout(4):
            assert await left.send_to(b"abcdef", right.local_endpoint) == 6
            small = await right.recv_from(3)
            assert small.payload == b"abc"
            assert small.truncated is True
            assert small.source == left.local_endpoint

            assert await left.send_to(b"", right.local_endpoint) == 0
            empty = await right.recv_from(0)
            assert empty.payload == b""
            assert empty.truncated is False

            await right.send_to(b"ping", left.local_endpoint)
            message = await left.recv_from(20)
            assert message.payload == b"ping"
            assert message.truncated is False
    finally:
        await left.aclose()
        await right.aclose()


@pytest.mark.asyncio
async def test_udp_pending_receive_cancelled_on_close() -> None:
    channel = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    task = asyncio.create_task(channel.recv_from(64))
    await asyncio.sleep(0)
    await channel.aclose()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(task, 2)
    await channel.aclose()
    with pytest.raises(StreamClosedError):
        await channel.recv_from(4)


@pytest.mark.asyncio
async def test_udp_validation_and_family_mismatch() -> None:
    channel = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    try:
        with pytest.raises(ValueError):
            await channel.recv_from(True)
        with pytest.raises(ValueError):
            await channel.recv_from(65536)
        with pytest.raises(TypeError):
            await channel.send_to("wrong", channel.local_endpoint)  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            await channel.send_to(b"foo", IPEndpoint.parse("::1", 9000))
        with pytest.raises(ValueError):
            await channel.send_to(b"foo", IPEndpoint.parse("127.0.0.1", 0))
    finally:
        await channel.aclose()
