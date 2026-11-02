# ADR-M2-07: Concurrency and failures

Status: Proposed for review in E00/E03/E04; not release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: One reader and one writer per stream, serialized using dedicated asyncio.Lock objects. Map operations after local close to StreamClosedError. OS transport exceptions retain their original chained context.

Consequences: contract and integration tests must enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
