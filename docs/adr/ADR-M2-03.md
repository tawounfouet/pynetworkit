# ADR-M2-03: Async UDP trunctation and ownership

Status: Accepted for M2 technical implementation on 2026-11-02; NOT release approval.

Context: M2 Async Core, Python >=3.11, hexagonal architecture. Existing M0/M1 code takes precedence over illustrative older docs.

Decision: Use nonblocking loop.sock_recvfrom(sock, 65535); slice the received bytes and expose ReceivedDatagram.truncated as len(raw)>max_bytes, including empty payload. One coroutine owns each socket operation, with explicit close.

Evidence: PRs #116-#121 with nine required CI checks each; see docs/audits/M2_EVIDENCE_LEDGER.md. Contract/integration tests enforce observable behavior; deviations require a revised ADR. No PyPI release is implied.
