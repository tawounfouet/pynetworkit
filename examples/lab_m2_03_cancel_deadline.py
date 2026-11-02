"""Demonstrate monotonic deadlines and explicit task cancellation."""

import asyncio

from pynetworkkit.application.deadlines import Deadline, within_deadline


async def main() -> None:
    deadline = Deadline.after(0.02)
    try:
        await within_deadline(asyncio.sleep(0.2), deadline)
    except TimeoutError:
        print("Expected timeout; no retries or orphaned tasks")

    cancelled = asyncio.Event()

    async def blocked() -> None:
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    task = asyncio.create_task(blocked())
    await asyncio.sleep(0)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    assert cancelled.is_set()
    print("Explicit cancellation propagated and cleaned up")


if __name__ == "__main__":
    asyncio.run(main())
