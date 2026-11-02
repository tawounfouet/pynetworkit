# ADR-M2-03: Async UDP trunctation and ownership

Status: Proposed for review in E00/E03/E04; not release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Use nonblocking loop.sock_recvfrom(sock, 65535); slice the received bytes and expose ReceivedDatagram.truncated as len(raw)>max_bytes, including empty payload. One coroutine owns each socket operation, with explicit close.

Consequences: contract and integration tests must enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
