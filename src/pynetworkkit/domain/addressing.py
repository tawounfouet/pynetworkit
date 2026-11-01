"""Immutable network value objects backed by the Python ipaddress module.

IPAddress and IPNetwork are type aliases. Parsing never performs DNS lookup.
IPv6 zone identifiers are deliberately rejected until their scope is modeled.
"""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import (
    IPv4Address,
    IPv4Network,
    IPv6Address,
    IPv6Network,
    ip_address,
    ip_network,
)
from typing import TypeAlias

from pynetworkkit.domain.errors import NetworkValidationError

IPAddress: TypeAlias = IPv4Address | IPv6Address
IPNetwork: TypeAlias = IPv4Network | IPv6Network


def parse_ip_address(value: str) -> IPAddress:
    """Parse an IP literal, rejecting DNS names and IPv6 zone identifiers."""
    if not isinstance(value, str):
        raise TypeError("IP address literal must be a string")
    if "%" in value:
        raise NetworkValidationError("IPv6 scope identifiers are unsupported in M0")
    try:
        return ip_address(value)
    except ValueError as exc:
        raise NetworkValidationError(f"Invalid IP address literal: {value!r}") from exc


def parse_ip_network(value: str, *, strict: bool = True) -> IPNetwork:
    """Parse a CIDR, with explicit strict host-bit semantics."""
    if not isinstance(value, str):
        raise TypeError("IP network literal must be a string")
    if not isinstance(strict, bool):
        raise TypeError("strict must be bool")
    if "%" in value:
        raise NetworkValidationError("IPv6 scope identifiers are unsupported in M0")
    try:
        return ip_network(value, strict=strict)
    except ValueError as exc:
        raise NetworkValidationError(f"Invalid IP network literal: {value!r}") from exc


@dataclass(frozen=True, slots=True)
class Port:
    """Port 0..65535, including 0 for an ephemeral local binding."""

    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int:
            raise TypeError("Port value must be an integer, excluding bool")
        if not 0 <= self.value <= 65535:
            raise NetworkValidationError("Port must be between 0 and 65535")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class IPEndpoint:
    """An immutable resolved address plus validated transport port."""

    address: IPAddress
    port: Port

    def __post_init__(self) -> None:
        if not isinstance(self.address, (IPv4Address, IPv6Address)):
            raise TypeError("Endpoint address must be IPv4Address or IPv6Address")
        if isinstance(self.address, IPv6Address) and self.address.scope_id is not None:
            raise NetworkValidationError("IPv6 scoped endpoints are unsupported in M0")
        if not isinstance(self.port, Port):
            raise TypeError("Endpoint port must be Port")

    @classmethod
    def parse(cls, address: str, port: int) -> IPEndpoint:
        """Build an endpoint from a numeric IP literal and port."""
        return cls(address=parse_ip_address(address), port=Port(port))

    def __str__(self) -> str:
        if isinstance(self.address, IPv6Address):
            return f"[{self.address}]:{self.port}"
        return f"{self.address}:{self.port}"
