# ADR-M2-08: Portability and qualification

Status: Accepted for M2 technical implementation on 2026-11-02; NOT release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: All network integration tests use loopback and ephemeral ports. IPv6 is capability-gated. CI runs Linux/macOS/Windows x Python 3.11, 3.12 and 3.13; final qualification is based on exact SHA evidence.

Evidence: PRs #116-#121 with nine required CI checks each; see docs/audits/M2_EVIDENCE_LEDGER.md. Contract/integration tests enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
