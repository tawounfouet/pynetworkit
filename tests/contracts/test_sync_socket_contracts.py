"""Run reusable synchronous transport contracts against real loopback sockets."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from pynetworkkit.adapters.socket import (
    SocketTCPConnector,
    SocketTCPListener,
    SocketTCPStream,
    SocketUDPChannel,
)
from pynetworkkit.domain import IPEndpoint
from tests.contracts.sync_transport_contracts import (
    assert_tcp_stream_contract,
    assert_udp_datagram_contract,
)


@contextmanager
def tcp_pair() -> Iterator[tuple[SocketTCPStream, SocketTCPStream]]:
    with SocketTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0)) as listener:
        with SocketTCPConnector().connect(listener.local_endpoint, timeout=2) as client:
            accepted, _ = listener.accept(timeout=2)
            with accepted:
                yield client, accepted


@contextmanager
def udp_pair() -> Iterator[tuple[SocketUDPChannel, SocketUDPChannel]]:
    local = IPEndpoint.parse("127.0.0.1", 0)
    with SocketUDPChannel.bind(local) as left, SocketUDPChannel.bind(local) as right:
        yield left, right


def test_reusable_tcp_contract() -> None:
    assert_tcp_stream_contract(tcp_pair)


def test_reusable_udp_contract() -> None:
    assert_udp_datagram_contract(udp_pair)
