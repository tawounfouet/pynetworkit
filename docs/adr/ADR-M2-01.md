# ADR-M2-01: Public API compatibility

Status: Accepted for M2 technical implementation on 2026-11-02; NOT release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Keep M0 read/write/aclose/connect(endpoint), and M1 sync types unmodified. Add only narrowly scoped listener/datagram capabilities. Do not turn TCP streams into message transports.

Evidence: PRs #116-#121 with nine required CI checks each; see docs/audits/M2_EVIDENCE_LEDGER.md. Contract/integration tests enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
