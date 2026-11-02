# ADR-M2-05: Monotonic deadline

Status: Proposed for review in E00/E03/E04; not release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Use asyncio event loop monotonic time and asyncio.timeout_at. Reuse a single absolute deadline across composed operations; do not reset it per attempt. A timeout is not EOF.

Consequences: contract and integration tests must enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
