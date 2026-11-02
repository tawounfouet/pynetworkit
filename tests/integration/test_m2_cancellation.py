"""Cancellation invariants for TCP read and UDP receive on localhost."""

import asyncio

import pytest

from pynetworkkit.adapters.asyncio import (
    AsyncioTCPConnector,
    AsyncioTCPListener,
    AsyncioUDPChannel,
)
from pynetworkkit.domain import IPEndpoint


@pytest.mark.asyncio
async def test_tcp_read_cancellation_does_not_close_owned_stream() -> None:
    listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
    client = None
    server = None
    try:
        async with asyncio.timeout(4):
            client = await AsyncioTCPConnector().connect(listener.local_endpoint)
            server, _ = await listener.accept()
            task = asyncio.create_task(server.read(32))
            await asyncio.sleep(0)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            await client.write(b"ok")
            assert await server.read(2) == b"ok"
    finally:
        if client is not None:
            await client.aclose()
        if server is not None:
            await server.aclose()
        await listener.aclose()


@pytest.mark.asyncio
async def test_udp_receive_cancellation_keeps_socket_usable() -> None:
    source = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    target = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    try:
        async with asyncio.timeout(4):
            task = asyncio.create_task(target.recv_from(10))
            await asyncio.sleep(0)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            await source.send_to(b"ok", target.local_endpoint)
            assert (await target.recv_from(10)).payload == b"ok"
    finally:
        await source.aclose()
        await target.aclose()
