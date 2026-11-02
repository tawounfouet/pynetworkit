# PyNetworkKit M2 - Technical Closure and GO/NO-GO

**Date:** 2026-11-02
**Milestone:** M2 - Async Core (`0.2.0a1`)
**Track:** D (development and technical qualification)
**Release Track:** R (separate, unapproved)
**Status:** Qualified technical implementation - final closure gate requires this document's merge and post-merge main CI.

## 1. Executive decision

**GO for M2 technical capabilities**, grounded in main SHA
`d29d686a5fb01c8d5161e1a5fe6051967dfa0d12`, its full 9/9 matrix
and its independent nonpublishing security candidate audit. The final
technical closure is recorded only after the last issue `PNK-M2-036`,
the E05 Epic, and the post-closure main SHA are verified.

**NO-GO for publishing to PyPI, creating a Git tag or GitHub Release.**
Those are independent G6 publication decisions. In particular, the
historic M1 candidate `0.1.0a2`, SHA provenance and issues #29/#67
are not superseded or auto-approved.

## 2. Verified implementation

| Epic | Functional result | Evidence |
| --- | --- | --- |
| E00 | Preserved `AsyncByteStream.read/write/aclose`, connector `connect(endpoint)` and sync M1 contracts; added listener/UDP async ports | PR #116 |
| E01 | Nonblocking TCP connector/stream/pull listener, partial reads, EOF, drain and socket ownership | PR #117 |
| E02 | Nonblocking UDP with peer metadata, empty payload and portable truncation | PR #118 |
| E03 | Cooperative cancellation, monotonic absolute deadlines and ownership tests | PR #119, #122 |
| E04 | Byte/item-bounded queue, backpressure, TaskGroup worker limits | PR #120 |
| E05 | Contract test reuse, IPv4/IPv6 capability-gated localhost, six labs, documentation, security/packaging audit | PR #121, #123 |

Design: hexagonal ports and adapters, ISP, DIP, DDD value objects,
structured concurrency and explicit resource ownership. The domain and
ports have no asyncio/OS networking imports. There is no private event
loop, custom TCP/IP stack, DNS implementation, HTTP, TLS or new mandatory dependency.

## 3. Exact-SHA qualification

**M2 candidate main SHA:** `d29d686a5fb01c8d5161e1a5fe6051967dfa0d12`.

- [CI 41525452114](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525452114): **9 of 9 quality jobs successful** across Linux/macOS/Windows and Python 3.11/3.12/3.13.
- [M2 security candidate audit 41525452563](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525452563): **successful**, Python 3.11 Ubuntu, **240 tests passed** and **97.54% combined branch coverage**, >=95% required.
- `pip-audit --local` found **no known vulnerabilities in the dependencies it could audit**; the local, unpublished `pynetworkkit` distribution was skipped as unavailable on PyPI. This does not certify the source against all possible defects.
- Ruff lint/format, strict mypy, repository hygiene, build, Twine metadata, isolated wheel install and `pip check` passed.
- `sha256sum -c` reported both `pynetworkkit-0.2.0a1-py3-none-any.whl: OK` and `pynetworkkit-0.2.0a1.tar.gz: OK`.
- [Candidate artifacts and SHA256 manifest](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525452563/artifacts/13178973173), with 14-day retention (until 2026-11-16).
- Module-level audit: TCP 93%, UDP 93%, bounded queues 100%, deadlines 100%, combined 97.54%. The two async OS adapters retain untested defensive error branches, accepted as residual test debt for alpha, not claims of 100% branch coverage.

No internet connections are used by transport integration tests; all TCP/UDP exchanges use localhost with ephemeral ports. Security audit dependency lookup is a separate controlled CI step.

## 4. Semantic invariants and failure behavior

- TCP delivers ordered **bytes**, not application message boundaries; `b""` on positive read means EOF.
- UDP retains message boundaries, empty datagrams, `ReceivedDatagram.source`, and `truncated` metadata. There is no UDP EOF or guaranteed delivery/order.
- Accepted TCP streams have independent ownership from the listener. Socket cleanup occurs on normal exit, error or cancellation.
- Cancellation/timeout propagates. An interrupted TCP write may have queued a prefix and cannot be retried blindly.
- Deadlines are absolute monotonic budgets, not per-stage resets.
- `BoundedByteQueue` enforces bytes and items limits, and `bounded_map` enforces an explicit upper bound on worker tasks. A slow consumer blocks a producer rather than permitting unbounded queues.
- No public half-close API was added to M0 `AsyncByteStream`; it is explicitly deferred.

## 5. Governance and evidence

The M2 issue structure includes 6 parent Epics (#73-#78) and 36 child tasks
(#79-#114). At the report drafting checkpoint, 5 Epics and 35 tasks
are technically closed; the last issue `#114` and E05 `#78` close
after this report is merged and the final SHA passes CI.

Eight ADRs `ADR-M2-01` through `ADR-M2-08` are accepted for the
technical scope, **not** publication. See
[`M2_EVIDENCE_LEDGER.md`](../audits/M2_EVIDENCE_LEDGER.md)
for all PR heads, merged SHAs and exact runs.

GitHub Project v2 #9 continues to be the canonical project tracker.
Native Issue states are verifiable. The three M2 views and Project
Status fields require a separate Project-scoped `--verify` inspection,
which is outside current connector access. No fabricated Project
Status or dates are reported.

## 6. Residual risks and mitigation

| Risk | Treatment |
| --- | --- |
| Unexercised OS-specific error branches (async TCP/UDP ~93%) | Maintain negative-path tests and expand fault injection in maintenance |
| Windows and IPv6 platform variations | Keep 9/9 matrix; IPv6 tests capability-gated rather than falsely mandatory |
| Event-loop backpressure not a delivery guarantee | Preserve drain/partial-write semantics and avoid automatic retries |
| Provider/project metadata not available through current token | Audit Project #9 with Project-scoped GitHub CLI verification |
| Supply-chain registry/publication approval | G6 NO-GO until explicit authorisation and release workflow evidence |

## 7. G0-G6 decisions

| Gate | Result | Notes |
| --- | --- | --- |
| G0 Bootstrap | GO | 6 Epics, 36 tasks and native parent/child tracking present |
| G1 Contracts | GO | Existing M0/M1 API preserved; ADR 01-03 accepted |
| G2 TCP/UDP | GO | Nonblocking loopback, tests and 9CI |
| G3 Cancellation/ownership | GO | Cancel injection, deadline, cleanup tests |
| G4 Backpressure | GO | Bounded byte/item/task resources and tests |
| G5 Technical closure | GO conditional on final report PR merge, issue reconciliation and final-main CI | Candidate evidence at SHA d29 qualified |
| G6 Publication | NO-GO | No tag/release/PyPI upload; G6 is an independent security and approval action |

## 8. Lessons and handoff

Evidence-based incremental PRs avoided changing historic M0/M1 contracts.
A shared stream test suite checks observed semantics, while independent
UDP contract tests preserve message differences. Queue byte credits and
TaskGroup concurrency caps make overload behavior explicit.

M3 - Protocol Utilities may now build on the verified M2 ports for DNS
resolution, bounded framing and codecs. See
[`31_PYNETWORKKIT_M3_HANDOFF_FROM_M2.md`](../roadmap/31_PYNETWORKKIT_M3_HANDOFF_FROM_M2.md).
M3 must not silently turn TCP into messages or bypass M2 cancellation
and resource ownership contracts.

**Final caveat:** this document records the candidate SHA, not the SHA
generated by merging this report itself. The latter requires a post-merge
CI run and evidence comment on issue #114, which is the final technical
closure event.
