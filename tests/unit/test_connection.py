"""Full state transition matrix for the pure ConnectionState model."""

from itertools import product

import pytest

import pynetworkkit.domain as network


ALLOWED = {
    (network.ConnectionState.CREATED, network.ConnectionState.CONNECTING),
    (network.ConnectionState.CREATED, network.ConnectionState.CLOSED),
    (network.ConnectionState.CONNECTING, network.ConnectionState.ESTABLISHED),
    (network.ConnectionState.CONNECTING, network.ConnectionState.CLOSING),
    (network.ConnectionState.CONNECTING, network.ConnectionState.FAILED),
    (network.ConnectionState.ESTABLISHED, network.ConnectionState.CLOSING),
    (network.ConnectionState.ESTABLISHED, network.ConnectionState.FAILED),
    (network.ConnectionState.CLOSING, network.ConnectionState.CLOSED),
    (network.ConnectionState.CLOSING, network.ConnectionState.FAILED),
}


@pytest.mark.parametrize("source,target", list(product(network.ConnectionState, repeat=2)))
def test_complete_transition_matrix(source: network.ConnectionState, target: network.ConnectionState) -> None:
    expected = (source, target) in ALLOWED
    assert network.can_transition(source, target) is expected
    if expected:
        assert network.transition_state(source, target) is target
    else:
        with pytest.raises(network.InvalidConnectionTransition, match="Invalid connection transition"):
            network.transition_state(source, target)


def test_connection_terminal_states_cannot_reopen() -> None:
    for terminal in (network.ConnectionState.CLOSED, network.ConnectionState.FAILED):
        assert all(not network.can_transition(terminal, candidate) for candidate in network.ConnectionState)


def test_repeated_close_is_not_a_state_transition() -> None:
    with pytest.raises(network.InvalidConnectionTransition):
        network.transition_state(network.ConnectionState.CLOSED, network.ConnectionState.CLOSED)


def test_reject_invalid_state_types() -> None:
    with pytest.raises(TypeError):
        network.can_transition("created", network.ConnectionState.CONNECTING)  # type: ignore[arg-type]
