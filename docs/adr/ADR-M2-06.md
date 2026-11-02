# ADR-M2-06: Backpressure / bounded resources

Status: Accepted for M2 technical implementation on 2026-11-02; NOT release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Use await writer.drain with bounded write chunks and deterministic concurrency caps. Queues specify maximum items and/or bytes; avoid unbounded per-client tasks and buffering.

Evidence: PRs #116-#121 with nine required CI checks each; see docs/audits/M2_EVIDENCE_LEDGER.md. Contract/integration tests enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
