"""The genuinely shared M0/M2 contract tested against memory and TCP."""

import asyncio

import pytest

from pynetworkkit.adapters.asyncio import AsyncioTCPConnector, AsyncioTCPListener
from pynetworkkit.adapters.memory import create_memory_stream_pair
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import AsyncByteStream


@pytest.mark.parametrize("backend", ["memory", "tcp"])
@pytest.mark.asyncio
async def test_common_stream_contract(backend: str) -> None:
    left: AsyncByteStream
    right: AsyncByteStream
    listener = None
    if backend == "memory":
        left, right = create_memory_stream_pair(max_buffer_bytes=64)
    else:
        listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
        left = await AsyncioTCPConnector().connect(listener.local_endpoint)
        right, _ = await listener.accept()
    try:
        async with asyncio.timeout(5):
            await left.write(b"")
            await left.write(b"abcde")
            received = bytearray()
            while len(received) < 5:
                data = await right.read(5 - len(received))
                assert data
                received.extend(data)
            assert bytes(received) == b"abcde"
            with pytest.raises(ValueError):
                await right.read(0)
            await left.aclose()
            assert await right.read(10) == b""
    finally:
        await left.aclose()
        await right.aclose()
        if listener is not None:
            await listener.aclose()
