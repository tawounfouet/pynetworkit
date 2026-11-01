"""Lab 03: deterministic, bounded async byte streams without real sockets."""

import asyncio

from pynetworkkit.adapters.memory import create_memory_stream_pair


async def exercise() -> None:
    """Exchange bytes in both directions; drain EOF and release resources."""
    left, right = create_memory_stream_pair(max_buffer_bytes=8)
    try:
        await left.write(b"hello")
        assert await right.read(2) == b"he"
        assert await right.read(3) == b"llo"
        await right.write(b"ok")
        assert await left.read(2) == b"ok"

        await left.aclose()
        assert await right.read(2) == b""
        print("lab03: bidirectional bytes, partial reads and EOF OK")
    finally:
        await left.aclose()
        await right.aclose()


def main() -> None:
    """Execute an asynchronous lab in a self-contained event loop."""
    asyncio.run(exercise())


if __name__ == "__main__":
    main()
