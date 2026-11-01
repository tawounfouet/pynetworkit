"""Property-based invariants for pure IPv4/IPv6 types and connection state.

Hypothesis examples use deterministic generation and avoid external network I/O.
"""

from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network

import pytest
from hypothesis import given, settings, strategies as st

from pynetworkkit.domain import (
    ConnectionState,
    IPEndpoint,
    InvalidConnectionTransition,
    Port,
    can_transition,
    parse_ip_address,
    parse_ip_network,
    transition_state,
)

MAX_IPV4 = (1 << 32) - 1
MAX_IPV6 = (1 << 128) - 1
PROPERTY_SETTINGS = settings(max_examples=75, derandomize=True, deadline=None)


@PROPERTY_SETTINGS
@given(value=st.integers(min_value=0, max_value=MAX_IPV4))
def test_ipv4_literal_roundtrip(value: int) -> None:
    address = IPv4Address(value)
    assert parse_ip_address(str(address)) == address


@PROPERTY_SETTINGS
@given(value=st.integers(min_value=0, max_value=MAX_IPV6))
def test_ipv6_literal_roundtrip(value: int) -> None:
    address = IPv6Address(value)
    assert parse_ip_address(str(address)) == address


@PROPERTY_SETTINGS
@given(
    address=st.integers(min_value=0, max_value=MAX_IPV4),
    prefix=st.integers(min_value=0, max_value=32),
)
def test_ipv4_network_normalizes_and_contains_host(address: int, prefix: int) -> None:
    host = IPv4Address(address)
    network = parse_ip_network(f"{host}/{prefix}", strict=False)
    assert network == IPv4Network((host, prefix), strict=False)
    assert host in network


@PROPERTY_SETTINGS
@given(
    address=st.integers(min_value=0, max_value=MAX_IPV6),
    prefix=st.integers(min_value=0, max_value=128),
)
def test_ipv6_network_normalizes_and_contains_host(address: int, prefix: int) -> None:
    host = IPv6Address(address)
    network = parse_ip_network(f"{host}/{prefix}", strict=False)
    assert network == IPv6Network((host, prefix), strict=False)
    assert host in network


@PROPERTY_SETTINGS
@given(number=st.integers(min_value=0, max_value=65535))
def test_port_is_immutable_value_and_hashable(number: int) -> None:
    left, right = Port(number), Port(number)
    assert left == right
    assert hash(left) == hash(right)
    assert str(left) == str(number)
    assert left.value == number


@PROPERTY_SETTINGS
@given(
    host=st.integers(min_value=0, max_value=MAX_IPV4),
    port=st.integers(min_value=0, max_value=65535),
)
def test_ipv4_endpoint_value_semantics(host: int, port: int) -> None:
    literal = str(IPv4Address(host))
    left = IPEndpoint.parse(literal, port)
    right = IPEndpoint(parse_ip_address(literal), Port(port))
    assert left == right
    assert hash(left) == hash(right)
    assert str(left) == f"{literal}:{port}"


@PROPERTY_SETTINGS
@given(
    host=st.integers(min_value=0, max_value=MAX_IPV6),
    port=st.integers(min_value=0, max_value=65535),
)
def test_ipv6_endpoint_bracketed_value_semantics(host: int, port: int) -> None:
    literal = str(IPv6Address(host))
    left = IPEndpoint.parse(literal, port)
    right = IPEndpoint(parse_ip_address(literal), Port(port))
    assert left == right
    assert hash(left) == hash(right)
    assert str(left) == f"[{literal}]:{port}"


@PROPERTY_SETTINGS
@given(states=st.lists(st.sampled_from(list(ConnectionState)), max_size=12))
def test_fsm_never_accepts_forbidden_transition(states: list[ConnectionState]) -> None:
    current = ConnectionState.CREATED
    for requested in states:
        if can_transition(current, requested):
            assert transition_state(current, requested) is requested
            current = requested
        else:
            with pytest.raises(InvalidConnectionTransition):
                transition_state(current, requested)
