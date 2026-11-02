"""M2 TCP: deterministic loopback, cancellation and resource ownership."""

import asyncio

import pytest

from pynetworkkit.adapters.asyncio import AsyncioTCPConnector, AsyncioTCPListener
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import StreamClosedError


@pytest.mark.asyncio
async def test_async_tcp_roundtrip_and_eof() -> None:
    listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
    client = None
    accepted = None
    try:
        async with asyncio.timeout(4):
            endpoint = listener.local_endpoint
            client = await AsyncioTCPConnector().connect(endpoint)
            accepted, remote = await listener.accept()
            assert remote.address.is_loopback
            await client.write(b"hello")
            assert await accepted.read(2) == b"he"
            assert await accepted.read(3) == b"llo"
            await accepted.write(b"world")
            assert await client.read(5) == b"world"
            await client.aclose()
            assert await accepted.read(10) == b""
    finally:
        if client is not None:
            await client.aclose()
        if accepted is not None:
            await accepted.aclose()
        await listener.aclose()


@pytest.mark.asyncio
async def test_tcp_close_is_idempotent_and_rejects_use() -> None:
    listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
    client = None
    accepted = None
    try:
        async with asyncio.timeout(4):
            client = await AsyncioTCPConnector().connect(listener.local_endpoint)
            accepted, _ = await listener.accept()
            await client.aclose()
            await client.aclose()
            with pytest.raises(StreamClosedError):
                await client.write(b"no")
            with pytest.raises(ValueError):
                await accepted.read(0)
            with pytest.raises(ValueError):
                await accepted.read(True)
            with pytest.raises(TypeError):
                await accepted.write("not bytes")  # type: ignore[arg-type]
    finally:
        if client is not None:
            await client.aclose()
        if accepted is not None:
            await accepted.aclose()
        await listener.aclose()


@pytest.mark.asyncio
async def test_pending_accept_cancelled_on_listener_close() -> None:
    listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
    task = asyncio.create_task(listener.accept())
    await asyncio.sleep(0)
    await listener.aclose()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(task, 2)
    await listener.aclose()


@pytest.mark.asyncio
async def test_tcp_refused_connection() -> None:
    listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
    remote = listener.local_endpoint
    await listener.aclose()
    async with asyncio.timeout(3):
        with pytest.raises(OSError):
            await AsyncioTCPConnector().connect(remote)
