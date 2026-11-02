# ADR-M2-04: Cancellation and resource lifetime

Status: Accepted for M2 technical implementation on 2026-11-02; NOT release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Propagate CancelledError, do not retry an operation after uncertain partial send. Close newly allocated and accepted sockets on every exception including cancellation. Closing is idempotent, and the listener does not own accepted streams.

Evidence: PRs #116-#121 with nine required CI checks each; see docs/audits/M2_EVIDENCE_LEDGER.md. Contract/integration tests enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
