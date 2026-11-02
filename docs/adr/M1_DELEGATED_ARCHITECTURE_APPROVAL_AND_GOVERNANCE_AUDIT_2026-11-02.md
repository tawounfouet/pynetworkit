# M1 - Delegated architecture approval and governance audit

- Review date: 2026-11-02
- Authority: explicit owner delegation in this conversation; approval is a
  delegated project decision, not a separate independent human review.
- Source reviewed: main SHA `7406ab35e00e35001ade8238c369f89919c157ed`
- CI evidence: https://github.com/tawounfouet/pynetworkkit/actions/runs/41459531092
- Implementation PR: https://github.com/tawounfouet/pynetworkkit/pull/66
- Technical closure PR: https://github.com/tawounfouet/pynetworkkit/pull/68

## Technical review findings

- M0 async ports stay separate from M1 blocking sync ports; the four
  Protocols define typed stream, connector, listener and datagram contracts.
- `SocketTCPStream.write()` returns a single positive partial-write count.
  `read()` returns b"" for TCP EOF, unlike the valid UDP b"" datagram.
- UDP `ReceivedDatagram` preserves source and truncation evidence, using
  a bounded 65535-byte full-datagram receive for Winsock compatibility.
- Connect/accept transfer resource ownership, and `close()` is idempotent.
- Timeout is operation-local; concurrent timeout changes on one socket are
  unsupported and no end-to-end deadline is promised.
- Contradiction found: ADR-M1-03/04 draft demanded a distinct listener/UDP
  locally-closed error, while the tested implementation uses the existing
  `StreamClosedError`. ADR amended to accept the actual common exception.
- ADR examples and outdated CI language have been reconciled with code.
- Current exact-main GitHub Actions: 9/9 passing across Linux/macOS/Windows
  and Python 3.11/3.12/3.13. Linux 3.11 reports 184 tests, 98.90% coverage.
  These are CI-derived measurements, not a local security penetration test.

## Architecture decisions

| Decision | Result | Limitation |
| --- | --- | --- |
| ADR-M1-01 | ACCEPTED | No write_all helper, no sync/async interchange |
| ADR-M1-02 | ACCEPTED | UDP full-size memory cap, no delivery guarantee |
| ADR-M1-03/04 | ACCEPTED AS AMENDED | Shared StreamClosedError; no concurrent timeout safety |
| ADR-M1-05/06 | ACCEPTED | Numeric IP only, no DNS, IPv6 capability-gated |

All approvals apply to the M1 technical design scope. They do not waive
security or release gates.

## Separate repository and release governance

Read-only GitHub repository audit on this date returned:
- `main.protected = false`.
- Active repository rulesets list: empty.
- GitHub Releases list: empty.
- Issue #29 (first M0 alpha publication) is open.
- Issue #67 (M1 release approval) was closed with unchecked conditions,
  so it needs separate reopening/reconciliation as a governance safeguard.

No branch-protection write capability was available through the connected
GitHub tool. This record does not pretend that required protections,
release hashes, registry checks or publication rights have been verified.
No tag, GitHub Release or PyPI upload is approved or performed.

## Closure logic

After merging this review and obtaining its exact-head CI, issue #37 can
be closed as M1 technical design approval (distinct from a release), then
the parent E00 Epic #31 once GitHub's five native children are closed.
A separate M1 release gate remains open until independent verification.
