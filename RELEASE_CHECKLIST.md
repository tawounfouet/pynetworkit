# M0 alpha candidate checklist - `0.1.0a1` (not yet released)

**Release state: NO-GO.** These are release obligations, not assertions that
a proposed tag or published artifact already exists.

## Evidence from branch and main CI

- [x] Repository, Python distribution and import use `pynetworkkit`.
- [x] E0, E1, E2 and E3 have passing nine-job CI evidence and are merged into `main`.
- [x] Existing domain properties, async contract checks and the 95% coverage
  floor are exercised in E3 CI.
- [x] E4 branch passed executable labs, isolated wheel checks and SHA256
  artifact collection on its previous head SHA.
- [ ] Qualify the final E4 head and the resulting merged `main` SHA.

## Blockers to resolve before tagging or publishing

- [x] MIT license chosen and committed with SPDX PEP 639 metadata.
- [ ] Confirm license expression and LICENSE inclusion in final merged-main distributions.
- [ ] Review repository `main` protection and required checks.
- [ ] Accept/reject all ADRs with documented rationale and maintainer approval.
- [ ] Approve reviewed public API and compatibility caveats.
- [ ] Review dependency-security posture and publication permission scope.
- [x] Merge E0 -> E1 -> E2 -> E3 in dependency order.
- [ ] Integrate E4 and qualify the resulting merged `main` SHA.
- [ ] Re-run full CI (nine jobs) and fresh wheel install on merged `main`.
- [ ] Record exact approved commit SHA, wheel/sdist hashes and evidence links.
- [ ] Sign the M0 GO/NO-GO review, approve a specific tag separately.
- [ ] Approve external GitHub Release / PyPI publication separately.

## Release candidate process (when authorized)

1. Build `python -m build` from a clean tree.
2. Check metadata with `python -m twine check dist/*`.
3. Verify wheel in a fresh venv offline with
   `python scripts/verify_distribution.py`.
4. Check `release-evidence/SHA256SUMS.txt` against approved artifacts.
5. Create proposed `v0.1.0a1` tag **only after sign-off**.
6. Follow the controlled rollback and patch procedure in
   [the candidate gate](docs/releases/M0_ALPHA_RELEASE_READINESS.md).

**No tag, GitHub release or PyPI upload is requested by this checklist.**
