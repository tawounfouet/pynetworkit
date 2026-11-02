"""E00 shape and import regression checks; socket adapters are future E01/E02."""

from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError
from typing import get_type_hints

import pytest

from pynetworkkit import domain, ports
from pynetworkkit.domain import IPEndpoint, Port
from pynetworkkit.ports import (
    AsyncByteStream,
    AsyncStreamConnector,
    ReceivedDatagram,
    SyncByteStream,
    SyncDatagramChannel,
    SyncStreamConnector,
    SyncStreamListener,
)


def test_existing_m0_async_api_is_not_renamed() -> None:
    assert ports.AsyncByteStream is AsyncByteStream
    assert ports.AsyncStreamConnector is AsyncStreamConnector
    assert inspect.iscoroutinefunction(AsyncByteStream.read)
    assert inspect.iscoroutinefunction(AsyncByteStream.write)
    assert inspect.iscoroutinefunction(AsyncByteStream.aclose)
    assert domain.IPEndpoint is IPEndpoint
    assert domain.Port is Port


@pytest.mark.parametrize(
    ("port", "method"),
    [
        (SyncByteStream, "read"),
        (SyncByteStream, "write"),
        (SyncByteStream, "shutdown_write"),
        (SyncByteStream, "close"),
        (SyncStreamConnector, "connect"),
        (SyncStreamListener, "accept"),
        (SyncStreamListener, "close"),
        (SyncDatagramChannel, "send_to"),
        (SyncDatagramChannel, "recv_from"),
        (SyncDatagramChannel, "close"),
    ],
)
def test_all_m1_port_methods_are_synchronous(port: type, method: str) -> None:
    assert not inspect.iscoroutinefunction(getattr(port, method))


def test_sync_stream_write_returns_count_not_async_none() -> None:
    assert get_type_hints(SyncByteStream.write)["return"] is int
    assert get_type_hints(AsyncByteStream.write)["return"] is type(None)


def test_connector_and_listener_use_typed_endpoints() -> None:
    assert get_type_hints(SyncStreamConnector.connect)["remote"] is IPEndpoint
    assert (
        get_type_hints(SyncStreamListener.accept)["return"] == (tuple[SyncByteStream, IPEndpoint])
    )


def test_udp_returns_enriched_datagram() -> None:
    assert get_type_hints(SyncDatagramChannel.recv_from)["return"] is ReceivedDatagram


def test_all_resource_ports_define_context_manager_operations() -> None:
    for cls in (SyncByteStream, SyncStreamListener, SyncDatagramChannel):
        assert "__enter__" in cls.__dict__
        assert "__exit__" in cls.__dict__


def test_empty_udp_datagram_is_valid_and_not_eof() -> None:
    datagram = ReceivedDatagram(b"", IPEndpoint.parse("127.0.0.1", 5000), False)
    assert datagram.payload == b""
    assert not datagram.truncated
    assert datagram.source.port == Port(5000)


def test_truncated_datagram_is_explicit_and_immutable() -> None:
    received = ReceivedDatagram(b"ab", IPEndpoint.parse("::1", 1234), True)
    assert received.truncated
    with pytest.raises(FrozenInstanceError):
        received.truncated = False  # type: ignore[misc]


@pytest.mark.parametrize(
    ("payload", "source", "truncated"),
    [
        ("not bytes", IPEndpoint.parse("127.0.0.1", 1), False),
        (b"", "127.0.0.1", False),
        (b"", IPEndpoint.parse("127.0.0.1", 1), 1),
    ],
)
def test_datagram_result_rejects_invalid_types(
    payload: object, source: object, truncated: object
) -> None:
    with pytest.raises(TypeError):
        ReceivedDatagram(payload, source, truncated)  # type: ignore[arg-type]


def test_datagram_result_preserves_ipv6_and_hash_equality() -> None:
    endpoint = IPEndpoint.parse("2001:db8::1", 1000)
    left = ReceivedDatagram(b"data", endpoint, False)
    assert left == ReceivedDatagram(b"data", endpoint, False)
    assert hash(left) == hash(ReceivedDatagram(b"data", endpoint, False))
    assert str(left.source) == "[2001:db8::1]:1000"
