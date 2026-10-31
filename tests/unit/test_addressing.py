"""Domain invariants for IPv4/IPv6, CIDR, Port and IPEndpoint."""

from dataclasses import FrozenInstanceError
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network

import pytest

from pynetworkkit.domain import (
    IPEndpoint,
    NetworkValidationError,
    Port,
    parse_ip_address,
    parse_ip_network,
)


@pytest.mark.parametrize("value", ["0.0.0.0", "127.0.0.1", "192.0.2.1"])
def test_parse_ipv4_roundtrip(value: str) -> None:
    address = parse_ip_address(value)
    assert isinstance(address, IPv4Address)
    assert str(address) == value


@pytest.mark.parametrize("value", ["::1", "2001:db8::7", "::"])
def test_parse_ipv6_roundtrip(value: str) -> None:
    address = parse_ip_address(value)
    assert isinstance(address, IPv6Address)
    assert str(address) == value


@pytest.mark.parametrize("value", ["", "localhost", "999.1.1.1", "127.0.0", "fe80::1%eth0"])
def test_reject_bad_address_literals(value: str) -> None:
    with pytest.raises(NetworkValidationError):
        parse_ip_address(value)


def test_reject_non_text_address() -> None:
    with pytest.raises(TypeError):
        parse_ip_address(123)  # type: ignore[arg-type]


def test_strict_cidr_and_explicit_normalization() -> None:
    with pytest.raises(NetworkValidationError):
        parse_ip_network("192.0.2.14/24")
    assert parse_ip_network("192.0.2.14/24", strict=False) == IPv4Network("192.0.2.0/24")
    assert parse_ip_network("2001:db8::15/64", strict=False) == IPv6Network("2001:db8::/64")


def test_subnet_membership_preserves_family() -> None:
    v4 = parse_ip_network("192.0.2.0/24")
    v6 = parse_ip_network("2001:db8::/32")
    assert parse_ip_address("192.0.2.4") in v4
    assert parse_ip_address("192.0.3.1") not in v4
    assert parse_ip_address("2001:db8::a") in v6
    assert parse_ip_address("192.0.2.4") not in v6


@pytest.mark.parametrize(
    "value",
    ["bad", "192.0.2.0/33", "2001:db8::/129", "fe80::%eth0/64"],
)
def test_reject_bad_network_literals(value: str) -> None:
    with pytest.raises(NetworkValidationError):
        parse_ip_network(value)


def test_reject_non_text_network_and_non_bool_strict() -> None:
    with pytest.raises(TypeError):
        parse_ip_network(0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        parse_ip_network("192.0.2.0/24", strict="yes")  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, 1, 443, 65535])
def test_port_valid_bounds(value: int) -> None:
    port = Port(value)
    assert port.value == value
    assert str(port) == str(value)
    assert Port(value) == port
    assert hash(Port(value)) == hash(port)


@pytest.mark.parametrize("value", [-1, 65536, 99999])
def test_reject_port_out_of_bounds(value: int) -> None:
    with pytest.raises(NetworkValidationError):
        Port(value)


@pytest.mark.parametrize("value", [True, False, 1.0, "443", None])
def test_reject_non_integer_ports(value: object) -> None:
    with pytest.raises(TypeError):
        Port(value)  # type: ignore[arg-type]


def test_port_immutable() -> None:
    port = Port(443)
    with pytest.raises(FrozenInstanceError):
        port.value = 80  # type: ignore[misc]


def test_endpoint_ipv4_value_and_format() -> None:
    endpoint = IPEndpoint.parse("192.0.2.10", 443)
    assert str(endpoint) == "192.0.2.10:443"
    assert endpoint == IPEndpoint(parse_ip_address("192.0.2.10"), Port(443))
    assert hash(endpoint) == hash(IPEndpoint.parse("192.0.2.10", 443))


def test_endpoint_ipv6_brackets() -> None:
    endpoint = IPEndpoint.parse("2001:db8::1", 443)
    assert str(endpoint) == "[2001:db8::1]:443"
    assert endpoint != IPEndpoint.parse("192.0.2.1", 443)


def test_endpoint_immutable() -> None:
    endpoint = IPEndpoint.parse("::1", 443)
    with pytest.raises(FrozenInstanceError):
        endpoint.port = Port(80)  # type: ignore[misc]


def test_endpoint_rejects_scoped_ipv6() -> None:
    with pytest.raises(NetworkValidationError):
        IPEndpoint(IPv6Address("fe80::1%eth0"), Port(443))


@pytest.mark.parametrize(
    "address,port",
    [("localhost", 443), ("::1", -1), ("192.0.2.1", 65536)],
)
def test_endpoint_parse_rejects_invalid_input(address: str, port: int) -> None:
    with pytest.raises(NetworkValidationError):
        IPEndpoint.parse(address, port)


def test_endpoint_rejects_unvalidated_members() -> None:
    with pytest.raises(TypeError):
        IPEndpoint("127.0.0.1", Port(443))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        IPEndpoint(IPv4Address("127.0.0.1"), 443)  # type: ignore[arg-type]
