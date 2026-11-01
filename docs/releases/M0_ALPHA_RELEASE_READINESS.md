# M0 alpha candidate validation and GO / NO-GO ledger

- Product: **PyNetworkKit** - `tawounfouet/pynetworkkit`
- Version target: `0.1.0a1`, proposed tag `v0.1.0a1`
- Status: **NO-GO for tagging or publication**, pending release approvals.
- Stage: code integration and release-gate verification.
- Evidence must refer to the exact tested `main` SHA before release approval.

## Meaning of "candidate"

The alpha **code and packaging** are prepared for validation, but there is no
approved Git tag, GitHub Release or PyPI publication. The term "candidate"
here is a staged *proposal*, not evidence that an alpha has shipped.

## Integration and qualification sequence

The M0 E0 [PR #5](https://github.com/tawounfouet/pynetworkkit/pull/5),
E1 [PR #11](https://github.com/tawounfouet/pynetworkkit/pull/11),
E2 [PR #16](https://github.com/tawounfouet/pynetworkkit/pull/16)
and E3 [PR #21](https://github.com/tawounfouet/pynetworkkit/pull/21)
have merged into `main` in dependency order.

E4 [PR #25](https://github.com/tawounfouet/pynetworkkit/pull/25)
contains the final documentation and candidate validation. Qualify the
resulting merged `main` SHA with fresh CI; prior feature-branch results
do not certify the new SHA.

## Candidate verification commands

```bash
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
mypy src/pynetworkkit
python scripts/check_repository_hygiene.py
python -m pytest -q --cov=pynetworkkit --cov-branch --cov-fail-under=95
python examples/lab01_ip_port.py
python examples/lab02_connection_fsm.py
python examples/lab03_memory_duplex.py
python -m build
python -m twine check dist/*
python scripts/verify_distribution.py
```

The verifier checks the wheel contents, installs the *local* wheel into a
fresh temporary venv with `--no-index --no-deps`, imports and checks the
distribution without reaching PyPI, and records SHA256 of wheel/sdist.
It stores the manifest in `release-evidence/SHA256SUMS.txt`. Do not
publish these files or treat them as signed provenance without approval.

If a local `dist` directory contains several builds, clean it first, then
rebuild to avoid mixing candidates. No release secret is used by CI.

## Gate status ledger

| Gate | Status at E4 bootstrap | Evidence or blocker |
| --- | --- | --- |
| Canonical repository and package name | PASS | `pynetworkkit` on GitHub |
| E0-E3 code + test qualification | PASS | All PRs merged; CI green |
| E4 docs execution | PASS | E4 merged; 121 tests, 9/9 CI green on main |
| Isolated wheel import + dist hashes | PASS | Verified on main CI 41329729503 |
| License selected and recorded | PASS | MIT, PEP 639 metadata and wheel inclusion tested on main |
| GitHub `main` protected / required checks | NOT VERIFIED | Repo-admin review required |
| ADRs 0001-0004 accepted or explicitly decided | PENDING | [ADR decision ledger](../adr/M0_DECISION_REGISTER.md) |
| M0 implementation task reconciliation | TRACKED | Deliverables verified; see [technical closure report](M0_TECHNICAL_CLOSURE_2026-11-01.md); release approval separate |
| Release readiness review | BLOCKED | Maintainer GO/NO-GO required |
| Tag `v0.1.0a1` | NOT CREATED | No tagging before approval |
| GitHub Release / PyPI | NOT PUBLISHED | Separate explicit permission required |

**Decision: NO-GO for release publication or tag.**
The successful technical CI of stacked PRs is not release approval.

## Supply-chain and release precautions

- Record wheel/sdist SHA256 and associated commit SHA in the evidence ledger.
- Verify `License-Expression: MIT`, `License-File: LICENSE`, and a bundled
  copy of LICENSE in both distributions; final merged-main proof is required.
- Complete contributor/security policies, secret review, dependency review and
  optional stronger auditing prior to external distribution.
- Decide whether signed annotated tags and action SHA pinning are required.
- There must be no fake claim of a release, stable API or publication.

## Recovery and rollback plan

- On a failing candidate gate: stop, open an issue, patch on a branch and
  revalidate. Do not tag the failed candidate.
- If an unapproved tag was created: stop dependent publications and assess
  cleanup under maintainer governance; do not rewrite protected branch history.
- If a GitHub release is later found problematic: stop distribution and
  communicate a corrective release; follow GitHub release policy.
- If a PyPI version is later found defective: release a corrected version.
  PyPI version files are immutable; consider **yanking** a release when justified
  rather than assuming a published version can be overwritten.
- Never place secrets or credentials in evidence artifacts.

## Sign-off template

```text
Current main SHA:              PENDING
Approved candidate SHA:       PENDING
CI run and platform matrix:   PENDING
Wheel SHA256 / sdist SHA256:   PENDING
License decision:             MIT selected, final main verification pending
ADR review evidence:          PENDING
Repository protection:        PENDING
Security review:              PENDING
Reviewer/approver:            PENDING
Tag approval:                 NO
Publish approval:             NO
GO / NO-GO:                   NO-GO
```

The planned tag and publication remain manual and separate operations.

## M0 implementation closeout

See [M0 Technical Closure and Evidence Ledger](M0_TECHNICAL_CLOSURE_2026-11-01.md).
Technical implementation GO is independent from release authorization. Open governance gates are maintained in [PNK-REL-001](https://github.com/tawounfouet/pynetworkkit/issues/29).
