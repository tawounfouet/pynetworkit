# M0 alpha candidate checklist - `0.1.0a1` (not yet released)

**Release state: NO-GO.** These are release obligations, not assertions that
a proposed tag or published artifact already exists.

## Verified on stacked feature branches (not merged to main)

- [x] Repository, Python distribution and import use `pynetworkkit`.
- [x] E0, E1, E2 and E3 have passing nine-job GitHub Actions matrix evidence.
- [x] Existing domain properties, async contract checks and the 95% coverage
  floor are exercised in E3 CI.
- [ ] E4 runs its executable documentation and isolated wheel checks on
  the final head SHA; capture XML and SHA256 evidence.

## Blockers to resolve before tagging or publishing

- [ ] Choose and commit an appropriate LICENSE with matching package metadata.
- [ ] Review repository `main` protection and required checks.
- [ ] Accept/reject all ADRs with documented rationale and maintainer approval.
- [ ] Approve reviewed public API and compatibility caveats.
- [ ] Review dependency-security posture and publication permission scope.
- [ ] Merge E0 -> E1 -> E2 -> E3 -> E4 in dependency order.
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
