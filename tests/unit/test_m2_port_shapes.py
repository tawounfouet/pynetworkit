"""E00: keep M0/M1 stable while introducing narrow M2 contracts."""

from inspect import signature

from pynetworkkit.ports import (
    AsyncByteStream,
    AsyncDatagramChannel,
    AsyncStreamConnector,
    AsyncStreamListener,
    ReceivedDatagram,
    SyncByteStream,
    SyncDatagramChannel,
)


def test_m0_async_signatures_remain_intact() -> None:
    assert list(signature(AsyncByteStream.read).parameters) == ["self", "max_bytes"]
    assert list(signature(AsyncByteStream.write).parameters) == ["self", "data"]
    assert list(signature(AsyncByteStream.aclose).parameters) == ["self"]
    assert list(signature(AsyncStreamConnector.connect).parameters) == ["self", "endpoint"]


def test_m1_sync_surface_remains_separate() -> None:
    assert callable(SyncByteStream.read)
    assert callable(SyncDatagramChannel.recv_from)
    assert list(signature(ReceivedDatagram).parameters) == ["payload", "source", "truncated"]


def test_m2_ports_have_small_distinct_capabilities() -> None:
    assert list(signature(AsyncStreamListener.accept).parameters) == ["self"]
    assert list(signature(AsyncDatagramChannel.recv_from).parameters) == ["self", "max_bytes"]
    assert list(signature(AsyncDatagramChannel.send_to).parameters) == [
        "self",
        "payload",
        "destination",
    ]
