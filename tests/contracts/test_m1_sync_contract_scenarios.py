"""Executable M1/E00 requirements on minimal fake transports, not OS adapters.

These doubles exercise the pre-adapter contract tests. They are deliberately
small and cannot establish runtime correctness of future socket adapters.
"""
from __future__ import annotations

from types import TracebackType
from typing import Self

import pytest

from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import ReceivedDatagram, StreamClosedError, SyncByteStream


class _ContractByteStream:
    def __init__(self, payload: bytes = b"") -> None:
        self._pending = payload
        self._closed = False
        self._write_closed = False

    def read(self, max_bytes: int) -> bytes:
        if type(max_bytes) is not int or max_bytes <= 0:
            raise ValueError("positive integer required")
        if self._closed:
            raise StreamClosedError("closed")
        chunk, self._pending = self._pending[:max_bytes], self._pending[max_bytes:]
        return chunk

    def write(self, data: bytes) -> int:
        if not isinstance(data, bytes):
            raise TypeError("bytes required")
        if self._closed or self._write_closed:
            raise StreamClosedError("closed")
        return min(2, len(data))

    def shutdown_write(self) -> None:
        if self._closed:
            raise StreamClosedError("closed")
        self._write_closed = True

    def close(self) -> None:
        self._closed = True

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


def _consume_stream(stream: SyncByteStream) -> tuple[bytes, int]:
    return stream.read(2), stream.write(b"abc")


def test_sync_stream_contract_partial_read_and_partial_write() -> None:
    stream: SyncByteStream = _ContractByteStream(b"abc")
    assert _consume_stream(stream) == (b"ab", 2)
    assert stream.read(2) == b"c"
    assert stream.read(1) == b""


@pytest.mark.parametrize("size", [0, -1, True])
def test_sync_stream_contract_rejects_bad_read_size(size: int) -> None:
    stream: SyncByteStream = _ContractByteStream()
    with pytest.raises(ValueError):
        stream.read(size)


def test_sync_stream_contract_half_close_keeps_read_open() -> None:
    stream: SyncByteStream = _ContractByteStream(b"ok")
    stream.shutdown_write()
    assert stream.read(2) == b"ok"
    with pytest.raises(StreamClosedError):
        stream.write(b"bad")


def test_sync_stream_contract_close_idempotence_and_ownership() -> None:
    stream: SyncByteStream = _ContractByteStream()
    stream.close()
    stream.close()
    with pytest.raises(StreamClosedError):
        stream.read(1)
    with pytest.raises(StreamClosedError):
        stream.write(b"x")


def test_sync_stream_context_manager_closes_on_error() -> None:
    stream = _ContractByteStream()
    with pytest.raises(ZeroDivisionError):
        with stream:
            raise ZeroDivisionError
    with pytest.raises(StreamClosedError):
        stream.read(1)


def test_truncated_udp_datagram_is_already_consumed() -> None:
    # A fake receive buffer models the intended one-shot max_bytes + 1 probe.
    payloads = [b"abcdefgh", b""]
    source = IPEndpoint.parse("127.0.0.1", 9000)

    def receive(max_bytes: int) -> ReceivedDatagram:
        if not (type(max_bytes) is int and 0 <= max_bytes <= 65535):
            raise ValueError("invalid receive limit")
        raw = payloads.pop(0)
        probe = raw[: max_bytes + 1]
        return ReceivedDatagram(probe[:max_bytes], source, len(probe) > max_bytes)

    first = receive(3)
    assert first.payload == b"abc" and first.truncated
    second = receive(3)
    assert second.payload == b"" and not second.truncated
    assert payloads == []


def test_udp_zero_capacity_distinguishes_empty_from_nonempty() -> None:
    src = IPEndpoint.parse("::1", 9000)
    empty = ReceivedDatagram(b"", src, False)
    nonempty = ReceivedDatagram(b"", src, True)
    assert empty != nonempty
