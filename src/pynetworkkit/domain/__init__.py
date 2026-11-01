"""Pure network domain: address, port, endpoint and lifecycle invariants."""

from pynetworkkit.domain.addressing import (
    IPAddress,
    IPEndpoint,
    IPNetwork,
    Port,
    parse_ip_address,
    parse_ip_network,
)
from pynetworkkit.domain.connection import (
    ConnectionState,
    can_transition,
    transition_state,
)
from pynetworkkit.domain.errors import (
    InvalidConnectionTransition,
    NetworkDomainError,
    NetworkValidationError,
)

__all__ = [
    "IPAddress",
    "IPEndpoint",
    "IPNetwork",
    "Port",
    "parse_ip_address",
    "parse_ip_network",
    "ConnectionState",
    "can_transition",
    "transition_state",
    "InvalidConnectionTransition",
    "NetworkDomainError",
    "NetworkValidationError",
]
