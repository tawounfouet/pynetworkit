"""M2 lab: failures after local close are typed and deterministic."""

import asyncio

from pynetworkkit.adapters.asyncio import AsyncioTCPListener, AsyncioUDPChannel
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import StreamClosedError


async def main() -> None:
    tcp = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
    udp = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
    await tcp.aclose()
    await udp.aclose()
    for action in [tcp.accept, lambda: udp.recv_from(128)]:
        try:
            await action()
        except StreamClosedError:
            pass
        else:
            raise AssertionError("closed endpoint must refuse new operations")
    print("lab_m2_06: explicit close semantics OK")


if __name__ == "__main__":
    asyncio.run(main())
