# M1 architecture decision register

Status: ACCEPTED for M1 technical baseline on 2026-11-02 by delegated project-owner review. These are architecture decisions, not release approvals.

| Decision | Document | Scope | Approval |
| --- | --- | --- | --- |
| ADR-M1-01 | [0005](0005-m1-sync-ports-and-partial-io.md) | Four separate ports, TCP partial writes and EOF | ACCEPTED |
| ADR-M1-02 | [0006](0006-m1-udp-boundaries-and-truncation.md) | UDP full packet bounded receive, typed truncation | ACCEPTED |
| ADR-M1-03/04 | [0007](0007-m1-ownership-timeouts-and-errors.md) | socket ownership, timeouts, OSError | ACCEPTED |
| ADR-M1-05/06 | [0008](0008-m1-ipv6-and-test-double-policy.md) | IPv6 scope and synchronous test doubles | ACCEPTED |

These decisions were accepted through explicit owner delegation after review
of source code, contracts, technical evidence and documented limitations.
The earlier CI success alone was not treated as architecture approval.
M0 ADR-0001..0004 are not modified or automatically accepted.

## Pending quality/architecture checks

- [x] Review operation-local temporary socket timeout mutation and
      concurrency restriction in production use.
- [x] Approve 65535-byte bounded UDP receive to avoid Winsock WSAEMSGSIZE.
- [x] Decide whether SyncByteStream should expose optional helper write_all.
      Current policy: no helper in the minimal port.
- [x] Approve close and half-close semantics separately from async aclose.
- [x] Review IP family and scoped IPv6 limitations.
- [x] Review the exact merged-main CI and packaging evidence after integration.

The technical M1 completion decision must remain distinct from explicit
release approval, tag creation, and PyPI publication.

## Recorded decision - 2026-11-02

- Decision authority: project owner delegated architecture review and approval
  in the PyNetworkKit conversation. Recorded by Pythos as delegated reviewer,
  not as an independent human code-reviewer or an external audit.
- ADR-M1-01: ACCEPTED. Separate sync Protocols, typed endpoints, explicit
  partial TCP writes, EOF and half-close. M0 async API is preserved.
- ADR-M1-02: ACCEPTED. Full bounded UDP receive then caller-visible slice;
  explicit ReceivedDatagram.truncated. Cross-platform tradeoff documented.
- ADR-M1-03/04: ACCEPTED AS AMENDED. Exclusive handle ownership, per-operation
  timeout restoration, idempotent close. Reuse StreamClosedError for all locally
  closed resources. No concurrency safety or overall deadline is implied.
- ADR-M1-05/06: ACCEPTED. Numeric IPv4/IPv6 endpoint model, capability-gated
  IPv6 loopback and explicit testing doubles; no DNS or universal simulator.
- Evidence: merged PR #66 and #68, final main code/documentation SHA
  7406ab35e00e35001ade8238c369f89919c157ed, CI #41459531092
  (9/9 jobs success; Linux Python 3.11: 184 tests, 98.90% coverage).
- Non-approval: branch protection, supply-chain publication checks, package
  registry credentials, release tags, GitHub Releases or PyPI publishing.
  Those remain independent in issues #29 and #67.
