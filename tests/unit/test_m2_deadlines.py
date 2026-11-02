"""Absolute budgets and validation can be checked with a fake clock."""

import asyncio

import pytest

from pynetworkkit.application.deadlines import Deadline, within_deadline


def test_deadline_remains_absolute_across_stages() -> None:
    now = [10.0]

    def clock() -> float:
        return now[0]

    deadline = Deadline.after(5, clock=clock)
    assert deadline.at == 15
    now[0] = 13.0
    assert deadline.remaining(clock=clock) == 2
    now[0] = 20.0
    assert deadline.remaining(clock=clock) == 0


@pytest.mark.parametrize("invalid", [-1.0, float("inf"), float("nan")])
def test_invalid_relative_deadlines(invalid: float) -> None:
    with pytest.raises(ValueError):
        Deadline.after(invalid, clock=lambda: 1.0)


def test_bool_rejected() -> None:
    with pytest.raises(TypeError):
        Deadline.after(True, clock=lambda: 1.0)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_absolute_timeout_propagates_and_cancels() -> None:
    cancelled = asyncio.Event()

    async def operation() -> None:
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    deadline = Deadline.after(0.01)
    with pytest.raises(TimeoutError):
        await within_deadline(operation(), deadline)
    assert cancelled.is_set()


@pytest.mark.asyncio
async def test_shared_deadline_success() -> None:
    assert await within_deadline(asyncio.sleep(0, result=42), Deadline.after(1)) == 42
