"""Reusable synchronous TCP/UDP behavioral contracts for adapter factories."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager

from pynetworkkit.ports import (
    SyncByteStream,
    SyncDatagramChannel,
)


def assert_tcp_stream_contract(
    pair: Callable[[], AbstractContextManager[tuple[SyncByteStream, SyncByteStream]]],
) -> None:
    """Check ordered bytes, bounded reads, partial-write handling and EOF."""
    with pair() as (left, right):
        payload = b"message-boundaries-are-not-preserved"
        pos = 0
        while pos < len(payload):
            accepted = left.write(payload[pos:], timeout=2)
            assert 0 < accepted <= len(payload) - pos
            pos += accepted
        left.shutdown_write()
        received = bytearray()
        while True:
            part = right.read(3, timeout=2)
            if not part:
                break
            received.extend(part)
        assert bytes(received) == payload


def assert_udp_datagram_contract(
    pair: Callable[[], AbstractContextManager[tuple[SyncDatagramChannel, SyncDatagramChannel]]],
) -> None:
    """Check empty datagram, source and observable truncation."""
    with pair() as (left, right):
        target = right.local_endpoint
        assert left.send_to(b"hello", target, timeout=2) == 5
        received = right.recv_from(2, timeout=2)
        assert received.payload == b"he"
        assert received.truncated
        assert received.source == left.local_endpoint
        assert left.send_to(b"", target, timeout=2) == 0
        zero = right.recv_from(2, timeout=2)
        assert zero.payload == b"" and not zero.truncated
        assert left.send_to(b"ok", target, timeout=2) == 2
        exact = right.recv_from(2, timeout=2)
        assert exact.payload == b"ok" and not exact.truncated
