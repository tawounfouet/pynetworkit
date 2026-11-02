# PyNetworkKit M1 - Technical qualification and release readiness

- Milestone: M1 Socket Kernel, target 0.1.0a2
- Status: technical code GO on exact merged-main SHA; release approval remains NO-GO
- Work: issues #36-#60, Epics #31-#35
- PR in review: https://github.com/tawounfouet/pynetworkkit/pull/66
- Scope: transport contracts, TCP/UDP adapters, lifecycle and 3 runnable labs.

## Exit checks

- [x] Complete CI on an exact merged-main SHA, not only feature branch.
- [x] Python 3.11, 3.12, 3.13 on ubuntu/macOS/Windows: 9/9 passing.
- [x] Strict Ruff lint/format and mypy of package source.
- [x] At least 95% combined statement/branch coverage and bounded tests.
- [x] IPv4 TCP/UDP loopback runs on all 9 jobs.
- [x] Capability-gated IPv6 TCP/UDP loopback; skip rationale documented.
- [x] Negative cases: bind conflict, connect refused, accept/read/recv
      timeout, send-zero, partial write, empty/oversized UDP datagrams.
- [x] Correct resource cleanup on construction errors and close, no
      permanent threads or external hosts.
- [x] All six learning labs runnable and included in CI (M0 + M1).
- [x] Wheel/sdist build, SPDX license, isolated offline wheel import and
      SHA256 candidate manifest.
- [x] Confirm M0 async API names and runtime semantics unchanged.
- [ ] Review ADR-M1-01..06 with maintainer and record decisions.
- [ ] Reconcile M1 work issues, PR evidence and milestone.
- [ ] Independently approve a specific release/tag candidate, if desired.

## Separate publication governance

M0 issue #29 (unapproved v0.1.0a1 publication) is not closed or bypassed
by M1 technical completion. M1 candidate release approval requires a
distinct explicit GO and exact SHA, artifact hashes, repository protections
and security review. A version string is never evidence of publication.

## Final evidence placeholders

- M1 merged main SHA: `4124b54a6e9e3a07b0ee590297211c889d0d2620`
- CI run URL: https://github.com/tawounfouet/pynetworkkit/actions/runs/41457849992
- Tests / coverage: 184 passed, 98.90% combined on Linux/Python 3.11; 9/9 jobs successful
- Artifact SHA256: SHA256SUMS.txt per-job CI artifact, 14-day retention; obtain immutable hashes before any release
- ADR sign-off: PENDING
- Technical GO/NO-GO: GO for implementation; NO-GO for tag/GitHub Release/PyPI
- Tag approval: NO
- GitHub Release/PyPI approval: NO
