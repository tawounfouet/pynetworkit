"""Composable absolute deadlines using the event loop monotonic clock."""

from __future__ import annotations

import asyncio
import math
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Deadline:
    """A fixed point on a monotonic clock, never reset between stages."""

    at: float

    def __post_init__(self) -> None:
        if isinstance(self.at, bool) or not isinstance(self.at, (int, float)):
            raise TypeError("deadline must be a finite number")
        if not math.isfinite(self.at):
            raise ValueError("deadline must be finite")

    @classmethod
    def after(cls, seconds: float, *, clock: Callable[[], float] | None = None) -> Deadline:
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
            raise TypeError("seconds must be a finite nonnegative number")
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError("seconds must be finite and nonnegative")
        monotonic = clock if clock is not None else asyncio.get_running_loop().time
        return cls(monotonic() + seconds)

    def remaining(self, *, clock: Callable[[], float] | None = None) -> float:
        monotonic = clock if clock is not None else asyncio.get_running_loop().time
        return max(0.0, self.at - monotonic())


async def within_deadline(operation: Awaitable[T], deadline: Deadline) -> T:
    """Execute under a shared absolute budget.

    This function never retries an operation after timeout. A partially
    completed network write may already have accepted some bytes.
    """
    async with asyncio.timeout_at(deadline.at):
        return await operation
