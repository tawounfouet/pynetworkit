# M1 architecture decision register

Status: TECHNICAL PROPOSAL - human maintainer sign-off required for acceptance.

| Decision | Document | Scope | Approval |
| --- | --- | --- | --- |
| ADR-M1-01 | [0005](0005-m1-sync-ports-and-partial-io.md) | Four separate ports, TCP partial writes and EOF | PROPOSED |
| ADR-M1-02 | [0006](0006-m1-udp-boundaries-and-truncation.md) | UDP full packet bounded receive, typed truncation | PROPOSED |
| ADR-M1-03/04 | [0007](0007-m1-ownership-timeouts-and-errors.md) | socket ownership, timeouts, OSError | PROPOSED |
| ADR-M1-05/06 | [0008](0008-m1-ipv6-and-test-double-policy.md) | IPv6 scope and synchronous test doubles | PROPOSED |

Technical CI proving an implementation is not itself architecture acceptance.
Before labeling an ADR accepted, record maintainer decision, date, rationale
and any required change. Do not silently alter existing M0 ADR-0001..0004.

## Pending quality/architecture checks

- [ ] Review operation-local temporary socket timeout mutation and
      concurrency restriction in production use.
- [ ] Approve 65535-byte bounded UDP receive to avoid Winsock WSAEMSGSIZE.
- [ ] Decide whether SyncByteStream should expose optional helper write_all.
      Current policy: no helper in the minimal port.
- [ ] Approve close and half-close semantics separately from async aclose.
- [ ] Review IP family and scoped IPv6 limitations.
- [ ] Review the exact merged-main CI and packaging evidence after integration.

The technical M1 completion decision must remain distinct from explicit
release approval, tag creation, and PyPI publication.
