"""Real IPv4/IPv6 UDP loopback, bounded receives and observable truncation."""
from __future__ import annotations

import socket

import pytest

from pynetworkkit.adapters.socket import SocketUDPChannel
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import StreamClosedError


def _exercise(host: str) -> None:
    local = IPEndpoint.parse(host, 0)
    with SocketUDPChannel.bind(local) as left, SocketUDPChannel.bind(local) as right:
        target = right.local_endpoint
        assert left.local_endpoint.port.value > 0
        assert left.send_to(b"alpha", target, timeout=1) == 5
        datagram = right.recv_from(5, timeout=1)
        assert datagram.payload == b"alpha"
        assert datagram.source == left.local_endpoint
        assert not datagram.truncated
        assert left.send_to(b"", target, timeout=1) == 0
        empty = right.recv_from(5, timeout=1)
        assert empty.payload == b""
        assert empty.truncated is False
        assert left.send_to(b"12345", target, timeout=1) == 5
        exact = right.recv_from(5, timeout=1)
        assert exact.payload == b"12345" and not exact.truncated
        assert left.send_to(b"123456", target, timeout=1) == 6
        clipped = right.recv_from(5, timeout=1)
        assert clipped.payload == b"12345" and clipped.truncated
        with pytest.raises(TimeoutError):
            right.recv_from(1, timeout=0.03)
        assert left.send_to(b"!", target, timeout=1) == 1
        zero = right.recv_from(0, timeout=1)
        assert zero.payload == b"" and zero.truncated
        assert left.send_to(b"", target, timeout=1) == 0
        empty_zero = right.recv_from(0, timeout=1)
        assert empty_zero.payload == b"" and not empty_zero.truncated
        with pytest.raises(ValueError):
            right.recv_from(-1)
        with pytest.raises(ValueError):
            right.recv_from(65536)
        with pytest.raises(ValueError):
            right.recv_from(True)
        with pytest.raises(TypeError):
            left.send_to("invalid", target)  # type: ignore[arg-type]
    left.close()
    right.close()
    with pytest.raises(StreamClosedError):
        right.recv_from(2, timeout=0.01)
    with pytest.raises(StreamClosedError):
        left.send_to(b"", IPEndpoint.parse(host, 5000))
    with pytest.raises(StreamClosedError):
        left.local_endpoint
    with pytest.raises(StreamClosedError):
        left.__enter__()


def test_udp_ipv4_loopback() -> None:
    _exercise("127.0.0.1")


def _supports_ipv6_udp() -> bool:
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as sock:
            sock.bind(("::1", 0))
        return True
    except OSError:
        return False


@pytest.mark.skipif(not _supports_ipv6_udp(), reason="IPv6 UDP loopback unavailable")
def test_udp_ipv6_loopback() -> None:
    _exercise("::1")


def test_udp_family_mismatch_and_bad_destination() -> None:
    with SocketUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0)) as channel:
        with pytest.raises(ValueError):
            channel.send_to(b"x", IPEndpoint.parse("::1", 9999))
        with pytest.raises(TypeError):
            channel.send_to(b"x", "localhost")  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            channel.send_to(b"x", channel.local_endpoint, timeout=float("nan"))
        with pytest.raises(ValueError):
            channel.recv_from(1, timeout=-1)


def test_udp_bind_occupied_and_context_exception() -> None:
    with pytest.raises(ZeroDivisionError):
        with SocketUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0)) as channel:
            with pytest.raises(OSError):
                SocketUDPChannel.bind(channel.local_endpoint)
            raise ZeroDivisionError
