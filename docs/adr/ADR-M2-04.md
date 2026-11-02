# ADR-M2-04: Cancellation and resource lifetime

Status: Proposed for review in E00/E03/E04; not release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Propagate CancelledError, do not retry an operation after uncertain partial send. Close newly allocated and accepted sockets on every exception including cancellation. Closing is idempotent, and the listener does not own accepted streams.

Consequences: contract and integration tests must enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
