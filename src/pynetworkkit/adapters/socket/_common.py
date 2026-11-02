"""Small OS-socket boundary helpers; never imported by the pure domain or ports."""
from __future__ import annotations

import math
import socket
from contextlib import contextmanager
from typing import Iterator

from pynetworkkit.domain import IPEndpoint, NetworkValidationError, Port, parse_ip_address


def address_family(endpoint: IPEndpoint) -> socket.AddressFamily:
    """Select the address family without DNS resolution."""
    if not isinstance(endpoint, IPEndpoint):
        raise TypeError("endpoint must be IPEndpoint")
    return socket.AF_INET6 if endpoint.address.version == 6 else socket.AF_INET


def socket_address(endpoint: IPEndpoint) -> tuple[str, int] | tuple[str, int, int, int]:
    if not isinstance(endpoint, IPEndpoint):
        raise TypeError("endpoint must be IPEndpoint")
    if endpoint.address.version == 6:
        return str(endpoint.address), endpoint.port.value, 0, 0
    return str(endpoint.address), endpoint.port.value


def endpoint_from_sockaddr(address: tuple[object, ...]) -> IPEndpoint:
    """Handle both IPv4 2-tuples and IPv6 4-tuples, without resolving names."""
    if len(address) not in (2, 4):
        raise NetworkValidationError("Unsupported socket address tuple")
    host, port = address[:2]
    if not isinstance(host, str) or type(port) is not int:
        raise NetworkValidationError("Invalid socket address members")
    return IPEndpoint(parse_ip_address(host), Port(port))


def validate_timeout(timeout: float | None) -> float | None:
    """None means blocking; zero means immediate/non-blocking OS behavior."""
    if timeout is None:
        return None
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise TypeError("timeout must be a finite nonnegative number or None")
    value = float(timeout)
    if not math.isfinite(value) or value < 0:
        raise ValueError("timeout must be finite and nonnegative")
    return value


@contextmanager
def temporary_timeout(sock: socket.socket, timeout: float | None) -> Iterator[None]:
    """Temporarily set a per-operation timeout, restoring previous socket mode.

    The socket must have one logical owner. Concurrent operations on the same
    socket cannot safely use different timeouts; callers must serialize them.
    """
    timeout = validate_timeout(timeout)
    original = sock.gettimeout()
    if timeout == original:
        yield
        return
    sock.settimeout(timeout)
    try:
        yield
    finally:
        sock.settimeout(original)


def enable_ipv6_only(sock: socket.socket, family: socket.AddressFamily) -> None:
    """Require single-family IPv6 sockets where the flag is available."""
    if family == socket.AF_INET6 and hasattr(socket, "IPV6_V6ONLY"):
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
