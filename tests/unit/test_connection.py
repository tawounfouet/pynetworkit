"""Full state transition matrix for the pure ConnectionState model."""

from itertools import product

import pytest

from pynetworkkit.domain.connection import ConnectionState, can_transition, transition_state
from pynetworkkit.domain.errors import InvalidConnectionTransition

ALLOWED = {
    (ConnectionState.CREATED, ConnectionState.CONNECTING),
    (ConnectionState.CREATED, ConnectionState.CLOSED),
    (ConnectionState.CONNECTING, ConnectionState.ESTABLISHED),
    (ConnectionState.CONNECTING, ConnectionState.CLOSING),
    (ConnectionState.CONNECTING, ConnectionState.FAILED),
    (ConnectionState.ESTABLISHED, ConnectionState.CLOSING),
    (ConnectionState.ESTABLISHED, ConnectionState.FAILED),
    (ConnectionState.CLOSING, ConnectionState.CLOSED),
    (ConnectionState.CLOSING, ConnectionState.FAILED),
}


@pytest.mark.parametrize("source,target", list(product(ConnectionState, repeat=2)))
def test_complete_transition_matrix(source: ConnectionState, target: ConnectionState) -> None:
    expected = (source, target) in ALLOWED
    assert can_transition(source, target) is expected
    if expected:
        assert transition_state(source, target) is target
    else:
        with pytest.raises(InvalidConnectionTransition, match="Invalid connection transition"):
            transition_state(source, target)


def test_connection_terminal_states_cannot_reopen() -> None:
    for terminal in (ConnectionState.CLOSED, ConnectionState.FAILED):
        assert all(not can_transition(terminal, candidate) for candidate in ConnectionState)


def test_repeated_close_is_not_a_state_transition() -> None:
    with pytest.raises(InvalidConnectionTransition):
        transition_state(ConnectionState.CLOSED, ConnectionState.CLOSED)


def test_reject_invalid_state_types() -> None:
    with pytest.raises(TypeError):
        can_transition("created", ConnectionState.CONNECTING)  # type: ignore[arg-type]
