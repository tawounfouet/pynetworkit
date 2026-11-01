"""Lab 02: enumerate valid connection transitions and reject an illegal edge."""

from pynetworkkit.domain import (
    ConnectionState,
    InvalidConnectionTransition,
    transition_state,
)


def main() -> None:
    """Model a connection lifecycle without a real network."""
    state = ConnectionState.CREATED
    for next_state in (
        ConnectionState.CONNECTING,
        ConnectionState.ESTABLISHED,
        ConnectionState.CLOSING,
        ConnectionState.CLOSED,
    ):
        state = transition_state(state, next_state)
    assert state is ConnectionState.CLOSED

    try:
        transition_state(ConnectionState.CLOSED, ConnectionState.ESTABLISHED)
    except InvalidConnectionTransition:
        print("lab02: lifecycle and rejected transition OK")
    else:
        raise AssertionError("Terminal connection state must not reopen")


if __name__ == "__main__":
    main()
