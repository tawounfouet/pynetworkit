"""M2 lab: empty datagrams and observable truncation (localhost only)."""

import asyncio

from pynetworkkit.adapters.asyncio import AsyncioUDPChannel
from pynetworkkit.domain import IPEndpoint


async def main() -> None:
    sender = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    receiver = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    try:
        async with asyncio.timeout(3):
            await sender.send_to(b"network", receiver.local_endpoint)
            value = await receiver.recv_from(3)
            print(value.payload, value.truncated, value.source)
            assert value.payload == b"net" and value.truncated
            await sender.send_to(b"", receiver.local_endpoint)
            assert (await receiver.recv_from(0)).payload == b""
    finally:
        await sender.aclose()
        await receiver.aclose()


if __name__ == "__main__":
    asyncio.run(main())
