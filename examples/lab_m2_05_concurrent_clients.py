"""Ten TCP loopback clients through bounded structured concurrency."""

import asyncio

from pynetworkkit.adapters.asyncio import AsyncioTCPConnector, AsyncioTCPListener
from pynetworkkit.application.bounded import bounded_map
from pynetworkkit.domain import IPEndpoint


async def main() -> None:
    listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
    endpoint = listener.local_endpoint

    async def server() -> None:
        for _ in range(10):
            stream, _ = await listener.accept()
            try:
                payload = await stream.read(32)
                await stream.write(payload)
            finally:
                await stream.aclose()

    async def client(index: int) -> int:
        stream = await AsyncioTCPConnector().connect(endpoint)
        try:
            message = str(index).encode()
            await stream.write(message)
            assert await stream.read(32) == message
            return index
        finally:
            await stream.aclose()

    try:
        async with asyncio.timeout(8):
            async with asyncio.TaskGroup() as group:
                server_task = group.create_task(server())
                result_task = group.create_task(bounded_map(list(range(10)), client, max_tasks=3))
            assert server_task.done()
            assert result_task.result() == list(range(10))
            print("lab_m2_05: ten bounded TCP clients OK")
    finally:
        await listener.aclose()


if __name__ == "__main__":
    asyncio.run(main())
