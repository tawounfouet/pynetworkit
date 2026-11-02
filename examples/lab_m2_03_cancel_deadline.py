"""Demonstrate a monotonic deadline and cooperative cancellation."""

import asyncio

from pynetworkkit.application.deadlines import Deadline, within_deadline


async def main() -> None:
    deadline = Deadline.after(0.02)
    try:
        await within_deadline(asyncio.sleep(0.2), deadline)
    except TimeoutError:
        print("Expected timeout; no retries or orphaned tasks")


if __name__ == "__main__":
    asyncio.run(main())
