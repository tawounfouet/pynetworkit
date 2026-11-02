# PyNetworkKit M1 - Socket Kernel technical closure and evidence ledger

- Date: 2026-11-02
- Milestone: M1 Socket Kernel, source version `0.1.0a2`
- Implementation scope: five Epics #31-#35, 25 issues #36-#60
- Implementation PR: [#66](https://github.com/tawounfouet/pynetworkkit/pull/66) (merged, squash)
- Exact audited `main` SHA: `4124b54a6e9e3a07b0ee590297211c889d0d2620`
- [Post-merge GitHub Actions CI](https://github.com/tawounfouet/pynetworkkit/actions/runs/41457849992): **9/9 completed SUCCESS**
- Linux/Python 3.11 job: **184 tests passed**, **98.90% combined
  statement/branch coverage**, threshold **95%**
- Decision: **TECHNICAL CODE GO**, **RELEASE/TAG NO-GO**
- Publication and architecture-governance issue:
  [#67](https://github.com/tawounfouet/pynetworkkit/issues/67)
- The earlier M0 release gate [#29](https://github.com/tawounfouet/pynetworkkit/issues/29)
  is unchanged. Neither `v0.1.0a1` nor `v0.1.0a2` is approved for publication.

## Delivered capabilities and evidence

| Epic | GitHub issues | Source and executable evidence |
| --- | --- | --- |
| E00 - Sync Transport Contracts | #36-#40 | `ports/sync_streams.py`, `ports/sync_datagrams.py`, `ReceivedDatagram`, M0 compatibility audit, ADRs |
| E01 - TCP Socket Adapters | #41-#45 | `adapters/socket/tcp.py`, TCP echo, IPv4/IPv6 loopback, EOF, half-close |
| E02 - UDP Datagram Adapters | #46-#50 | `adapters/socket/udp.py`, typed peer, empty datagrams, bounded truncation |
| E03 - Lifecycle and Ownership | #51-#55 | `_common.py`, context managers, ownership, bounded timeout, fault injection |
| E04 - Integration Tests & Labs | #56-#60 | reusable sync contracts, cross-OS tests, M1 labs, docs, wheel verification |

### M0 compatibility

M0 `AsyncByteStream.read/write/aclose`, `AsyncStreamConnector`,
`MemoryByteStream`, domain addressing and pure lifecycle semantics are
unchanged. New synchronous ports are structurally separate and import no
`socket` or `asyncio`. The typed domain is reused unchanged.
Source distribution version `0.1.0a2` identifies a development baseline,
not a release.

### Network semantics and resource handling

- TCP partial read/write, EOF, half-close and deterministic close behavior.
- Per-operation timeout validation and restoration; explicit documented
  restriction against concurrent timeout mutation of the same socket.
- Connector and listener transfer exclusive ownership. Temporary socket
  handles are cleaned on construction failures.
- UDP whole datagram semantics, valid empty payload, peer identity,
  observable truncation, no delivery or ordering guarantee.
- Winsock WSAEMSGSIZE fix: bounded full-datagram 65535-byte receive before
  applying the caller-visible max_bytes, independent of POSIX recvmsg.
- IPv4 required in CI; capability-gated IPv6 loopback with explicit skips.
- All tests use bounded loopback or deterministic doubles, no Internet I/O.

## Qualification matrix

| Gate | Evidence | Result |
| --- | --- | --- |
| Linux, macOS, Windows x Python 3.11, 3.12, 3.13 | Actions #41457849992 | PASS 9/9 |
| pytest on Linux 3.11 | Same run | PASS 184 tests |
| Combined branch/statement coverage | Same run | PASS 98.90%, minimum 95% |
| Ruff lint / Ruff format | Same run | PASS |
| mypy strict on src/pynetworkkit | Same run | PASS |
| Sync TCP/UDP loopback and failure injection | tests/integration, tests/unit, tests/contracts | PASS |
| M0 and M1 learning labs | tests/docs/test_learning_labs.py | PASS |
| Wheel/sdist, twine, isolated no-index wheel | scripts/verify_distribution.py | PASS |
| SPDX MIT and bundled LICENSE | wheel verifier | PASS |
| Per-job SHA256SUMS artifact | CI run artifacts | GENERATED (14-day retention) |
| ADR-M1-01..06 final maintainer acceptance | docs/adr/M1_DECISION_REGISTER.md | PENDING |
| Tag, release, PyPI permission | governance #67 | NOT AUTHORIZED |
| main branch protection / required checks | repository configuration | NOT VERIFIED AS PROTECTED |

## Verification commands

```bash
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
mypy src/pynetworkkit
python -m pytest -q --cov=pynetworkkit --cov-branch --cov-fail-under=95
python examples/lab_m1_01_tcp_echo.py
python examples/lab_m1_02_udp_datagram.py
python examples/lab_m1_03_fault_investigations.py
python -m build
python -m twine check dist/*
python scripts/verify_distribution.py
```

These commands were executed in GitHub CI on the audited main commit.
No local checkout claim is made by this report.

## Engineering decisions and caveats

- Expose synchronous ports rather than alter M0 async contracts.
- Do not implement generic DNS, TLS, HTTP or an OS-agnostic network simulator.
- `write_all()` is deliberately deferred, and TCP callers must handle
  partial writes with bounded loops.
- Dynamic IPv6 capability and dual-stack differences are documented.
- Passing memory-stream tests cannot substitute for real socket tests.
- Existing proposed ADR decisions require independent human acceptance.

## Issue reconciliation

PR #66 is merged. The 24 technical issues #36-#59 have evidence comments.
Issue #37 required a follow-up state check after an API-level write rejection;
issue #60 tracks final technical/release audit and is closed only after final
evidence reconciliation. Do not infer a 25/25 milestone closure from CI alone.
The five Epics should be closed only after all their implementation tasks
are verified complete.

## GO / NO-GO

- **GO:** M1 synchronous TCP/UDP code is implemented and qualified at the
  exact `main` SHA shown above, with 9/9 CI and 98.90% coverage.
- **NO-GO:** any `v0.1.0a2` tag, GitHub Release or PyPI upload, until the
  maintainer's separate governance decisions in issue #67.
- **Pending:** formal ADR-M1-01..06 acceptance and branch protection review.
  These are governance gates, not hidden technical test passes.

This technical closeout is not a statement of published software.
