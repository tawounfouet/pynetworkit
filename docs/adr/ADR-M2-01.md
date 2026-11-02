# ADR-M2-01: Public API compatibility

Status: Proposed for review in E00/E03/E04; not release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Keep M0 read/write/aclose/connect(endpoint), and M1 sync types unmodified. Add only narrowly scoped listener/datagram capabilities. Do not turn TCP streams into message transports.

Consequences: contract and integration tests must enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
