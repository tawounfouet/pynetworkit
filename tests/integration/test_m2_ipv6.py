"""M2 IPv6 loopback is capability-gated, never an external network test."""

import asyncio

import pytest

from pynetworkkit.adapters.asyncio import (
    AsyncioTCPConnector,
    AsyncioTCPListener,
    AsyncioUDPChannel,
)
from pynetworkkit.domain import IPEndpoint


@pytest.mark.asyncio
async def test_async_tcp_ipv6_if_available() -> None:
    try:
        listener = AsyncioTCPListener.bind(IPEndpoint.parse("::1", 0))
    except OSError as exc:
        pytest.skip(f"IPv6 loopback unavailable: {exc}")
    client = None
    peer = None
    try:
        async with asyncio.timeout(5):
            client = await AsyncioTCPConnector().connect(listener.local_endpoint)
            peer, remote = await listener.accept()
            assert remote.address.version == 6
            await client.write(b"v6")
            assert await peer.read(2) == b"v6"
    finally:
        if client is not None:
            await client.aclose()
        if peer is not None:
            await peer.aclose()
        await listener.aclose()


@pytest.mark.asyncio
async def test_async_udp_ipv6_if_available() -> None:
    try:
        left = AsyncioUDPChannel.bind(IPEndpoint.parse("::1", 0))
    except OSError as exc:
        pytest.skip(f"IPv6 loopback unavailable: {exc}")
    try:
        right = AsyncioUDPChannel.bind(IPEndpoint.parse("::1", 0))
    except OSError as exc:
        await left.aclose()
        pytest.skip(f"IPv6 loopback unavailable: {exc}")
    try:
        async with asyncio.timeout(5):
            await left.send_to(b"ipv6", right.local_endpoint)
            result = await right.recv_from(8)
            assert result.payload == b"ipv6"
            assert result.source.address.version == 6
            assert not result.truncated
    finally:
        await left.aclose()
        await right.aclose()
