"""Asynchronous UDP must preserve datagram boundaries and sender metadata."""

import asyncio

import pytest

from pynetworkkit.adapters.asyncio import AsyncioUDPChannel
from pynetworkkit.domain import IPEndpoint


@pytest.mark.asyncio
async def test_async_datagram_contract() -> None:
    sender = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    receiver = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    try:
        async with asyncio.timeout(3):
            await sender.send_to(b"abc", receiver.local_endpoint)
            a = await receiver.recv_from(3)
            assert a.payload == b"abc"
            assert not a.truncated
            assert a.source == sender.local_endpoint
            await sender.send_to(b"qwerty", receiver.local_endpoint)
            b = await receiver.recv_from(1)
            assert b.payload == b"q" and b.truncated
            await sender.send_to(b"z", receiver.local_endpoint)
            assert (await receiver.recv_from(10)).payload == b"z"
    finally:
        await sender.aclose()
        await receiver.aclose()
