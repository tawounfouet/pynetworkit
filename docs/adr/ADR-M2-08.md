# ADR-M2-08: Portability and qualification

Status: Proposed for review in E00/E03/E04; not release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: All network integration tests use loopback and ephemeral ports. IPv6 is capability-gated. CI runs Linux/macOS/Windows x Python 3.11, 3.12 and 3.13; final qualification is based on exact SHA evidence.

Consequences: contract and integration tests must enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
