"""Show producer wait when byte credits are exhausted (offline lab)."""

import asyncio

from pynetworkkit.application.bounded import BoundedByteQueue


async def main() -> None:
    queue = BoundedByteQueue(max_bytes=4, max_items=2)
    await queue.put(b"abcd")
    producer = asyncio.create_task(queue.put(b"ef"))
    await asyncio.sleep(0)
    print("producer blocked:", not producer.done(), "buffered:", queue.buffered_bytes)
    assert not producer.done()
    assert await queue.get() == b"abcd"
    await producer
    assert queue.buffered_bytes == 2
    await queue.aclose()


if __name__ == "__main__":
    asyncio.run(main())
