"""Lab 01: parse IP literals, validate ports and form endpoints.

Run from an editable installation: python examples/lab01_ip_port.py
This program never creates a socket or uses DNS.
"""

from pynetworkkit.domain import IPEndpoint, Port, parse_ip_address, parse_ip_network


def main() -> None:
    """Observe immutable addressing values and CIDR membership."""
    address = parse_ip_address("192.0.2.10")
    subnet = parse_ip_network("192.0.2.0/24")
    endpoint = IPEndpoint(address, Port(443))
    assert address in subnet
    assert str(endpoint) == "192.0.2.10:443"
    ipv6 = IPEndpoint.parse("2001:db8::1", 443)
    assert str(ipv6) == "[2001:db8::1]:443"
    print("lab01: IPv4 CIDR, Port, IPv6 endpoint OK")


if __name__ == "__main__":
    main()
