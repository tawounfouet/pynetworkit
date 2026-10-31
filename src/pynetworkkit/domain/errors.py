"""Typed errors for pure network-domain invariants."""


class NetworkDomainError(Exception):
    """Base exception for network-domain failures."""


class NetworkValidationError(NetworkDomainError, ValueError):
    """An address, network or port violates a domain invariant."""


class InvalidConnectionTransition(NetworkDomainError, ValueError):
    """A requested connection-state transition is forbidden."""
