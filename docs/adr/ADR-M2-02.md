# ADR-M2-02: Async TCP transport

Status: Accepted for M2 technical implementation on 2026-11-02; NOT release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Use asyncio.open_connection for clients. Use nonblocking loop.sock_accept for pull-based listener, then asyncio.open_connection(sock=accepted) to transfer ownership to StreamReader/StreamWriter. Never await blocking accept or connect.

Evidence: PRs #116-#121 with nine required CI checks each; see docs/audits/M2_EVIDENCE_LEDGER.md. Contract/integration tests enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
