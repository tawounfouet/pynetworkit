# ADR-M2-02: Async TCP transport

Status: Proposed for review in E00/E03/E04; not release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Use asyncio.open_connection for clients. Use nonblocking loop.sock_accept for pull-based listener, then asyncio.open_connection(sock=accepted) to transfer ownership to StreamReader/StreamWriter. Never await blocking accept or connect.

Consequences: contract and integration tests must enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
