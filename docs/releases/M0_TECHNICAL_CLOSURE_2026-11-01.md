# PyNetworkKit M0 - Technical Closure and Evidence Ledger

- Date: 2026-11-01
- Scope: M0 / E0-E4, implementation baseline only
- Source of truth: [GitHub repository](https://github.com/tawounfouet/pynetworkkit), branch `main`
- Initial audited SHA: `901422a02309f6776ee7ccc33107dc288339bbaa`
- [Audited GitHub Actions run](https://github.com/tawounfouet/pynetworkkit/actions/runs/41329729503)
- Version implemented: `0.1.0a1` package metadata, **not tagged or published**
- Decision: **GO for technical M0 completion and M1 design handoff**
- Decision: **NO-GO for creating a release tag, GitHub Release or PyPI publication**
- Maintainer's authorization for release: **not recorded**

## Evidence-based scope

| Epic | Merged PR | GitHub issues | Delivered baseline |
| --- | --- | --- | --- |
| E0 Repository & Packaging | [#5](https://github.com/tawounfouet/pynetworkkit/pull/5) | #1-#4 | src layout, packaging, MIT, CI baseline |
| E1 Domain Kernel | [#11](https://github.com/tawounfouet/pynetworkkit/pull/11) | #6-#10 | IP/CIDR, Port, Endpoint, ConnectionState |
| E2 Ports & Memory Adapter | [#16](https://github.com/tawounfouet/pynetworkkit/pull/16) | #12-#15 | async capability ports, bounded duplex memory stream, contract tests |
| E3 Verification & CI | [#21](https://github.com/tawounfouet/pynetworkkit/pull/21) | #17-#20 | Hypothesis, cancellation, hygiene, coverage, matrix |
| E4 Documentation & Release Readiness | [#25](https://github.com/tawounfouet/pynetworkkit/pull/25) | #22-#24 | quickstart, 3 offline labs, API docs, ADR register, wheel verifier |

All five implementation PRs are merged. The separate dependency maintenance PRs
[#26](https://github.com/tawounfouet/pynetworkkit/pull/26),
[#27](https://github.com/tawounfouet/pynetworkkit/pull/27), and
[#28](https://github.com/tawounfouet/pynetworkkit/pull/28) are also merged.

The 20 issues above represent M0 implementation and preparation deliverables.
The release governance exception is explicitly moved to
[PNK-REL-001 / issue #29](https://github.com/tawounfouet/pynetworkkit/issues/29).
Closure of an implementation issue means its documented and tested deliverable
is complete, **not** that tag/publication approval has been granted.

## Qualified M0 test and packaging matrix

| Gate | Result | Evidence |
| --- | --- | --- |
| Linux, macOS and Windows, Python 3.11, 3.12 and 3.13 | **PASS: 9/9** | [Actions run 41329729503](https://github.com/tawounfouet/pynetworkkit/actions/runs/41329729503) |
| pytest | **PASS: 121 tests** | Same CI run |
| Combined statement and branch coverage | **97.38%**, floor **95%** | Same CI run |
| Ruff lint/format and mypy strict | **PASS** | Same CI run |
| Three offline executable learning labs | **PASS** | `tests/docs/test_learning_labs.py` |
| Async contract and cancellation tests | **PASS** | `tests/contracts/` |
| Wheel and source distribution; twine metadata | **PASS** | Same CI run |
| Isolated wheel installation without PyPI | **PASS** | `scripts/verify_distribution.py` |
| SPDX MIT license and packaged LICENSE | **PASS** | `pyproject.toml`, root `LICENSE`, CI wheel inspection |
| Dependency integrity and heuristic credential hygiene | **PASS (limited)** | `pip check`, local secret heuristic |
| Public package registration, tag, release | **NOT DONE** | No release authorization |

No runtime third-party dependency was added in M0. M0 contains no real TCP/UDP
socket adapter, DNS client, TLS or remote network probe. A passing memory
adapter contract does not demonstrate correct real TCP behavior.

## Architecture decisions and remaining governance

ADRs [0001](../adr/0001-python-packaging-and-naming.md),
[0002](../adr/0002-domain-addressing-and-lifecycle.md),
[0003](../adr/0003-memory-stream-semantics.md), and
[0004](../adr/0004-e3-quality-gates.md) document **implemented decisions** but
retain their **PROPOSED** formal status until maintainer acceptance. This
closure report **does not** silently approve them.

The MIT choice and repository spelling are already authorized/implemented.
The following are not yet verified or approved:

1. `main` required checks/branch protection. GitHub App's protection GET
   returned 403; available ruleset list was empty. No protection is presumed.
2. Explicit acceptance/rejection of ADR-0001..0004 and public pre-alpha API,
   including CREATED/NEW, terminal FAILED, half-close and IPv6 scope policy.
3. Release security/supply chain review, package name confirmation, artifacts
   and hash sign-off for the **approved** candidate SHA.
4. Independent human decision to authorize `v0.1.0a1` tagging and publication.

All four are release-governance obligations in
[PNK-REL-001](https://github.com/tawounfouet/pynetworkkit/issues/29).
This is a **transparent technical closeout with a separate release NO-GO**,
not a certification that all release gates have passed.

## M0 to M1 handoff

The baseline for M1 - Socket Kernel (`0.1.0a2`) consists of:

- Pure address/CIDR/Port/IPEndpoint domain objects and state transition rules.
- `AsyncByteStream` and `AsyncStreamConnector` semantics as qualified in M0.
- In-process memory stream tests and reusable behavioral assertions.
- A CI quality floor and reproducible docs/packaging checks.

For M1, implement **separate synchronous** TCP/UDP capability contracts and
OS socket adapters; do not conflate the M0 async memory API with an actual TCP
implementation. Constrain integration tests to bounded loopback; keep domain
independent of the OS. Consult the proposed project document
`21_PYNETWORKKIT_M1_SOCKET_KERNEL_TASK_BREAKDOWN.md`. It proposes 25 tasks,
**not yet automatically created on GitHub**.

## Final decision

- **M0 / implementation completion: GO**, anchored to the audited main SHA.
- **Release `v0.1.0a1`: NO-GO** until [issue #29](https://github.com/tawounfouet/pynetworkkit/issues/29)
  has approvals and new exact-SHA candidate evidence.
- **M1 design/bootstrap preparation: GO**. No M1 socket work has been claimed.
- Technical closure PR and any subsequent merge SHA are a documentation
  change: re-run CI on the resulting main before using it as release evidence.
