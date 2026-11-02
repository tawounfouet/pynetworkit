"""Fault injection for socket construction, timeout restoration, partial I/O."""
from __future__ import annotations

import socket
from collections.abc import Iterator

import pytest

from pynetworkkit.adapters.socket._common import (
    address_family,
    endpoint_from_sockaddr,
    socket_address,
    temporary_timeout,
    validate_timeout,
)
from pynetworkkit.adapters.socket.tcp import (
    SocketTCPConnector,
    SocketTCPListener,
    SocketTCPStream,
)
from pynetworkkit.adapters.socket.udp import SocketUDPChannel
from pynetworkkit.domain import IPEndpoint, NetworkValidationError
from pynetworkkit.ports import StreamClosedError

LOCAL = IPEndpoint.parse("127.0.0.1", 0)
PEER = IPEndpoint.parse("127.0.0.1", 12345)


class FakeSocket:
    family = socket.AF_INET

    def __init__(self) -> None:
        self.timeout: float | None = None
        self.closed = 0
        self.events: list[str] = []
        self.fail: str = ""
        self.sent = 1
        self.raw: bytes = b"data"
        self.accepted: FakeSocket | None = None
        self.address: tuple[object, ...] = ("127.0.0.1", 12345)

    def gettimeout(self) -> float | None:
        return self.timeout

    def settimeout(self, value: float | None) -> None:
        self.timeout = value
        self.events.append("timeout")

    def connect(self, address: tuple[object, ...]) -> None:
        self.events.append("connect")
        if self.fail == "connect":
            raise ConnectionRefusedError("fake refused")

    def bind(self, address: tuple[object, ...]) -> None:
        self.events.append("bind")
        if self.fail == "bind":
            raise OSError("fake bind error")

    def listen(self, backlog: int) -> None:
        self.events.append("listen")
        if self.fail == "listen":
            raise OSError("fake listen error")

    def accept(self) -> tuple[FakeSocket, tuple[object, ...]]:
        if self.fail == "accept":
            raise OSError("fake accept error")
        assert self.accepted is not None
        return self.accepted, self.address

    def recv(self, max_bytes: int) -> bytes:
        if self.fail == "recv":
            raise OSError("fake read error")
        return self.raw[:max_bytes]

    def send(self, data: bytes) -> int:
        if self.fail == "send":
            raise OSError("fake send error")
        return self.sent

    def recvfrom(self, max_bytes: int) -> tuple[bytes, tuple[object, ...]]:
        if self.fail == "recvfrom":
            raise OSError("fake recv error")
        return self.raw[:max_bytes], self.address

    def sendto(self, data: bytes, address: tuple[object, ...]) -> int:
        if self.fail == "sendto":
            raise OSError("fake sendto error")
        return self.sent

    def getsockname(self) -> tuple[object, ...]:
        return self.address

    def getpeername(self) -> tuple[object, ...]:
        return self.address

    def shutdown(self, how: int) -> None:
        if self.fail == "shutdown":
            raise OSError("fake shutdown error")
        self.events.append("shutdown")

    def setsockopt(self, level: int, flag: int, value: int) -> None:
        self.events.append("setsockopt")

    def close(self) -> None:
        self.closed += 1


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), float("-inf")])
def test_timeout_rejects_invalid_numbers(value: float) -> None:
    with pytest.raises(ValueError):
        validate_timeout(value)


@pytest.mark.parametrize("value", ["1", True, object()])
def test_timeout_rejects_wrong_types(value: object) -> None:
    with pytest.raises(TypeError):
        validate_timeout(value)  # type: ignore[arg-type]


def test_timeout_none_and_zero_and_socket_restore() -> None:
    sock = FakeSocket()
    assert validate_timeout(None) is None
    assert validate_timeout(0) == 0.0
    with temporary_timeout(sock, None):  # type: ignore[arg-type]
        assert sock.events == []
    with temporary_timeout(sock, 0.1):  # type: ignore[arg-type]
        assert sock.timeout == 0.1
    assert sock.timeout is None
    with pytest.raises(ZeroDivisionError):
        with temporary_timeout(sock, 0):  # type: ignore[arg-type]
            assert sock.timeout == 0
            raise ZeroDivisionError
    assert sock.timeout is None


def test_sockaddr_invariants() -> None:
    assert socket_address(PEER) == ("127.0.0.1", 12345)
    assert socket_address(IPEndpoint.parse("::1", 80)) == ("::1", 80, 0, 0)
    assert address_family(IPEndpoint.parse("::1", 80)) == socket.AF_INET6
    assert endpoint_from_sockaddr(("::1", 22, 0, 0)) == IPEndpoint.parse("::1", 22)
    for bad in (("127.0.0.1",), ("127.0.0.1", "a"), (1, 80)):
        with pytest.raises(NetworkValidationError):
            endpoint_from_sockaddr(bad)
    with pytest.raises(NetworkValidationError):
        endpoint_from_sockaddr(("invalid", 80))
    with pytest.raises(TypeError):
        address_family("127.0.0.1")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        socket_address("127.0.0.1")  # type: ignore[arg-type]


def test_fake_stream_partial_zero_eof_error_and_close() -> None:
    fake = FakeSocket()
    stream = SocketTCPStream(fake)  # type: ignore[arg-type]
    assert stream.local_endpoint == PEER
    assert stream.remote_endpoint == PEER
    assert stream.read(100, timeout=0.1) == b"data"
    assert fake.timeout is None
    assert stream.write(b"abc", timeout=0.1) == 1
    assert stream.write(b"") == 0
    fake.sent = 0
    with pytest.raises(ConnectionError, match="progress"):
        stream.write(b"xxx")
    fake.sent = 4
    with pytest.raises(ConnectionError):
        stream.write(b"x")
    fake.fail = "send"
    with pytest.raises(OSError):
        stream.write(b"xx")
    fake.fail = "recv"
    with pytest.raises(OSError):
        stream.read(2)
    fake.fail = "shutdown"
    with pytest.raises(OSError):
        stream.shutdown_write()
    fake.fail = ""
    stream.shutdown_write()
    stream.shutdown_write()
    assert fake.events.count("shutdown") == 1
    with pytest.raises(StreamClosedError):
        stream.write(b"!")
    stream.close()
    stream.close()
    assert fake.closed == 1


def test_connector_frees_failed_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    sock = FakeSocket()
    sock.fail = "connect"
    monkeypatch.setattr(socket, "socket", lambda *args: sock)
    with pytest.raises(ConnectionRefusedError):
        SocketTCPConnector().connect(PEER, timeout=0.2)
    assert sock.closed == 1 and sock.timeout is None
    assert "connect" in sock.events


@pytest.mark.parametrize("phase", ["bind", "listen"])
def test_listener_frees_failed_socket(monkeypatch: pytest.MonkeyPatch, phase: str) -> None:
    sock = FakeSocket()
    sock.fail = phase
    monkeypatch.setattr(socket, "socket", lambda *args: sock)
    with pytest.raises(OSError):
        SocketTCPListener.bind(LOCAL)
    assert sock.closed == 1


def test_listener_accept_failure_and_bad_peer_close(monkeypatch: pytest.MonkeyPatch) -> None:
    sock, child = FakeSocket(), FakeSocket()
    sock.accepted = child
    listener = SocketTCPListener(sock)  # type: ignore[arg-type]
    sock.fail = "accept"
    with pytest.raises(OSError):
        listener.accept(timeout=0.1)
    assert sock.timeout is None
    sock.fail = ""
    sock.address = ("localhost", 1)
    with pytest.raises(NetworkValidationError):
        listener.accept(timeout=0.1)
    assert child.closed == 1
    listener.close()
    listener.close()
    assert sock.closed == 1


def test_udp_send_failure_short_write_and_recv_failure() -> None:
    sock = FakeSocket()
    channel = SocketUDPChannel(sock)  # type: ignore[arg-type]
    assert channel.local_endpoint == PEER
    sock.sent = 0
    with pytest.raises(OSError, match="entire"):
        channel.send_to(b"abc", PEER)
    sock.sent = 3
    assert channel.send_to(b"abc", PEER) == 3
    sock.fail = "sendto"
    with pytest.raises(OSError):
        channel.send_to(b"abc", PEER)
    sock.fail = "recvfrom"
    with pytest.raises(OSError):
        channel.recv_from(3, timeout=0.1)
    sock.fail = ""
    sock.raw = b"long"
    packet = channel.recv_from(2)
    assert packet.payload == b"lo" and packet.truncated
    channel.close()
    channel.close()
    assert sock.closed == 1


def test_udp_frees_failed_bind_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    sock = FakeSocket()
    sock.fail = "bind"
    monkeypatch.setattr(socket, "socket", lambda *args: sock)
    with pytest.raises(OSError):
        SocketUDPChannel.bind(LOCAL)
    assert sock.closed == 1


def test_udp_rejects_bad_local_type_and_validates_send_target() -> None:
    with pytest.raises(TypeError):
        SocketUDPChannel.bind("127.0.0.1")  # type: ignore[arg-type]
    sock = FakeSocket()
    channel = SocketUDPChannel(sock)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        channel.send_to(b"x", "127.0.0.1")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        channel.send_to(b"x", IPEndpoint.parse("::1", 80))
    channel.close()
