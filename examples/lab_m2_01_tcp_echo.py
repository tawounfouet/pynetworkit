"""Async TCP echo over localhost without application framing."""

import asyncio

from pynetworkkit.adapters.asyncio import AsyncioTCPConnector, AsyncioTCPListener
from pynetworkkit.domain import IPEndpoint


async def main() -> None:
    listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
    client = None
    server = None
    try:
        async with asyncio.timeout(4):
            client = await AsyncioTCPConnector().connect(listener.local_endpoint)
            server, _ = await listener.accept()
            await client.write(b"ping")
            chunks = bytearray()
            while len(chunks) < 4:
                chunk = await server.read(4 - len(chunks))
                assert chunk
                chunks.extend(chunk)
            await server.write(bytes(chunks))
            echoed = bytearray()
            while len(echoed) < 4:
                chunk = await client.read(4 - len(echoed))
                assert chunk
                echoed.extend(chunk)
            assert bytes(echoed) == b"ping"
            print("lab_m2_01: asynchronous TCP echo OK")
    finally:
        if client is not None:
            await client.aclose()
        if server is not None:
            await server.aclose()
        await listener.aclose()


if __name__ == "__main__":
    asyncio.run(main())
