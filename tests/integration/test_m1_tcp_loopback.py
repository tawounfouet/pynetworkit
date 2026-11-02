"""Bounded TCP loopback qualification without external network or permanent servers."""

from __future__ import annotations

import socket
import threading

import pytest

from pynetworkkit.adapters.socket import SocketTCPConnector, SocketTCPListener
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import StreamClosedError

LOOPBACK = IPEndpoint.parse("127.0.0.1", 0)


def _exchange(family_host: str) -> None:
    local = IPEndpoint.parse(family_host, 0)
    with SocketTCPListener.bind(local) as listener:
        assert listener.local_endpoint.port.value > 0
        connector = SocketTCPConnector()
        with connector.connect(listener.local_endpoint, timeout=2) as client:
            with pytest.raises(ValueError):
                client.read(0)
            with pytest.raises(TypeError):
                client.write("bad")  # type: ignore[arg-type]
            assert client.local_endpoint.port.value > 0
            assert client.remote_endpoint == listener.local_endpoint
            server, source = listener.accept(timeout=2)
            with server:
                assert source == client.local_endpoint
                assert server.local_endpoint == listener.local_endpoint
                assert server.remote_endpoint == source
                assert client.write(b"hello", timeout=2) > 0
                assert server.read(5, timeout=2) == b"hello"
                assert client.write(b"") == 0
                client.shutdown_write()
                client.shutdown_write()
                with pytest.raises(StreamClosedError):
                    client.write(b"x")
                assert server.read(1, timeout=2) == b""
                assert server.write(b"ok", timeout=2) == 2
                assert client.read(2, timeout=2) == b"ok"
            assert client.read(2, timeout=2) == b""
        client.close()
        with pytest.raises(StreamClosedError):
            client.read(1)
        with pytest.raises(StreamClosedError):
            client.write(b"x")
        with pytest.raises(StreamClosedError):
            client.shutdown_write()
        with pytest.raises(StreamClosedError):
            _ = client.local_endpoint
        with pytest.raises(StreamClosedError):
            _ = client.remote_endpoint
        with pytest.raises(StreamClosedError):
            client.__enter__()
    listener.close()
    with pytest.raises(StreamClosedError):
        listener.accept(timeout=0.02)
    with pytest.raises(StreamClosedError):
        _ = listener.local_endpoint
    with pytest.raises(StreamClosedError):
        listener.__enter__()


def test_tcp_full_duplex_and_half_close_ipv4() -> None:
    _exchange("127.0.0.1")


def _supports_ipv6_tcp() -> bool:
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
            sock.bind(("::1", 0))
        return True
    except OSError:
        return False


@pytest.mark.skipif(not _supports_ipv6_tcp(), reason="IPv6 loopback is unavailable")
def test_tcp_full_duplex_and_half_close_ipv6() -> None:
    _exchange("::1")


def test_listener_accept_timeout_and_refused_connect() -> None:
    with SocketTCPListener.bind(LOOPBACK) as listener:
        with pytest.raises(TimeoutError):
            listener.accept(timeout=0.03)
        with pytest.raises(OSError):
            SocketTCPListener.bind(listener.local_endpoint)
        refused = listener.local_endpoint
    # The listener's ephemeral port was released. A refused connection may
    # surface as any OSError subclass across supported operating systems.
    with pytest.raises(OSError):
        SocketTCPConnector().connect(refused, timeout=0.4)


def test_tcp_close_on_context_exception_and_remote_eof() -> None:
    with pytest.raises(ZeroDivisionError):
        with SocketTCPListener.bind(LOOPBACK) as listener:
            with SocketTCPConnector().connect(listener.local_endpoint, timeout=1) as client:
                server, _ = listener.accept(timeout=1)
                with server:
                    client.close()
                    assert server.read(1, timeout=1) == b""
                    raise ZeroDivisionError


def test_connector_rejects_port_zero_and_invalid_input() -> None:
    with pytest.raises(ValueError):
        SocketTCPConnector().connect(LOOPBACK)
    with pytest.raises(TypeError):
        SocketTCPConnector().connect("localhost")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        SocketTCPListener.bind(LOOPBACK, backlog=0)
    with pytest.raises(ValueError):
        SocketTCPListener.bind(LOOPBACK, backlog=True)
    with pytest.raises(ValueError):
        SocketTCPConnector().connect(IPEndpoint.parse("127.0.0.1", 1), timeout=-1)


def test_accept_does_not_own_accepted_socket() -> None:
    listener = SocketTCPListener.bind(LOOPBACK)
    client = SocketTCPConnector().connect(listener.local_endpoint, timeout=2)
    accepted, _ = listener.accept(timeout=2)
    try:
        listener.close()
        assert client.write(b"x", timeout=2) == 1
        assert accepted.read(1, timeout=2) == b"x"
    finally:
        accepted.close()
        client.close()
        listener.close()


def test_tcp_echo_with_bounded_thread_join() -> None:
    errors: list[Exception] = []
    with SocketTCPListener.bind(LOOPBACK) as listener:
        endpoint = listener.local_endpoint

        def serve() -> None:
            try:
                with listener.accept(timeout=2)[0] as stream:
                    while True:
                        chunk = stream.read(3, timeout=2)
                        if chunk == b"":
                            break
                        offset = 0
                        while offset < len(chunk):
                            offset += stream.write(chunk[offset:], timeout=2)
            except Exception as exc:
                errors.append(exc)

        worker = threading.Thread(target=serve)
        worker.start()
        try:
            with SocketTCPConnector().connect(endpoint, timeout=2) as client:
                message = b"hello socket kernel!"
                offset = 0
                while offset < len(message):
                    offset += client.write(message[offset:], timeout=2)
                client.shutdown_write()
                received = bytearray()
                while len(received) < len(message):
                    block = client.read(7, timeout=2)
                    assert block, "Premature TCP EOF"
                    received.extend(block)
                assert bytes(received) == message
        finally:
            worker.join(timeout=5)
            assert not worker.is_alive(), "TCP server thread leaked"
        assert errors == []
