"""Byte-bounded pipelines and task-bounded structured concurrency."""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Awaitable, Callable, Sequence
from typing import TypeVar, cast

from pynetworkkit.ports import StreamClosedError

T = TypeVar("T")
R = TypeVar("R")


class BoundedByteQueue:
    """A finite queue with separate byte and item limits.

    Outstanding items count towards both limits. Cancellation of a waiting
    producer never reserves capacity. Closing wakes all blocked consumers
    and producers; buffered items remain available to drain.
    """

    def __init__(self, *, max_bytes: int, max_items: int) -> None:
        if type(max_bytes) is not int or max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")
        if type(max_items) is not int or max_items <= 0:
            raise ValueError("max_items must be a positive integer")
        self._max_bytes = max_bytes
        self._max_items = max_items
        self._buffered = 0
        self._items: deque[bytes] = deque()
        self._closed = False
        self._changed = asyncio.Condition()

    @property
    def buffered_bytes(self) -> int:
        return self._buffered

    @property
    def qsize(self) -> int:
        return len(self._items)

    async def put(self, item: bytes) -> None:
        if not isinstance(item, bytes):
            raise TypeError("item must be bytes")
        if len(item) > self._max_bytes:
            raise ValueError("item exceeds queue byte capacity")
        async with self._changed:
            while not self._closed and (
                self._buffered + len(item) > self._max_bytes or len(self._items) >= self._max_items
            ):
                await self._changed.wait()
            if self._closed:
                raise StreamClosedError("queue is closed")
            self._items.append(item)
            self._buffered += len(item)
            self._changed.notify_all()

    async def get(self) -> bytes:
        async with self._changed:
            while not self._items and not self._closed:
                await self._changed.wait()
            if not self._items:
                raise StreamClosedError("queue is closed and empty")
            item = self._items.popleft()
            self._buffered -= len(item)
            self._changed.notify_all()
            return item

    async def aclose(self) -> None:
        async with self._changed:
            self._closed = True
            self._changed.notify_all()


async def bounded_map(
    items: Sequence[T],
    operation: Callable[[T], Awaitable[R]],
    *,
    max_tasks: int,
) -> list[R]:
    """Process items with at most max_tasks owned TaskGroup children.

    Results are returned in input order; O(len(items)) result memory is
    intentional, unlike the O(max_tasks) bound on concurrently live tasks.
    An error cancels siblings through TaskGroup and propagates as ExceptionGroup.
    """
    if type(max_tasks) is not int or max_tasks <= 0:
        raise ValueError("max_tasks must be a positive integer")
    if not items:
        return []
    sentinel = object()
    results: list[object] = [sentinel] * len(items)
    next_index = 0

    async def work() -> None:
        nonlocal next_index
        while next_index < len(items):
            index = next_index
            next_index += 1
            results[index] = await operation(items[index])

    async with asyncio.TaskGroup() as group:
        for _ in range(min(max_tasks, len(items))):
            group.create_task(work())
    return [cast(R, result) for result in results]
