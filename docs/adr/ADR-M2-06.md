# ADR-M2-06: Backpressure / bounded resources

Status: Proposed for review in E00/E03/E04; not release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Use await writer.drain with bounded write chunks and deterministic concurrency caps. Queues specify maximum items and/or bytes; avoid unbounded per-client tasks and buffering.

Consequences: contract and integration tests must enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
