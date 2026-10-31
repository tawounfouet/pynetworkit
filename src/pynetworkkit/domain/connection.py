"""Pure logical connection state machine, not kernel TCP state."""

from enum import Enum

from pynetworkkit.domain.errors import InvalidConnectionTransition


class ConnectionState(str, Enum):
    """States for one logical communication connection."""

    CREATED = "created"
    CONNECTING = "connecting"
    ESTABLISHED = "established"
    CLOSING = "closing"
    CLOSED = "closed"
    FAILED = "failed"


_ALLOWED: dict[ConnectionState, frozenset[ConnectionState]] = {
    ConnectionState.CREATED: frozenset({ConnectionState.CONNECTING, ConnectionState.CLOSED}),
    ConnectionState.CONNECTING: frozenset(
        {ConnectionState.ESTABLISHED, ConnectionState.CLOSING, ConnectionState.FAILED}
    ),
    ConnectionState.ESTABLISHED: frozenset(
        {ConnectionState.CLOSING, ConnectionState.FAILED}
    ),
    ConnectionState.CLOSING: frozenset({ConnectionState.CLOSED, ConnectionState.FAILED}),
    ConnectionState.CLOSED: frozenset(),
    ConnectionState.FAILED: frozenset(),
}


def can_transition(source: ConnectionState, target: ConnectionState) -> bool:
    """Return true exactly for permitted transitions."""
    if not isinstance(source, ConnectionState) or not isinstance(target, ConnectionState):
        raise TypeError("Both states must be ConnectionState values")
    return target in _ALLOWED[source]


def transition_state(source: ConnectionState, target: ConnectionState) -> ConnectionState:
    """Return valid next state or raise a typed domain exception."""
    if not can_transition(source, target):
        raise InvalidConnectionTransition(
            f"Invalid connection transition: {source.value} -> {target.value}"
        )
    return target
