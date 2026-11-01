# ADR-0004 - M0 quality evidence, property testing and CI security

- Status: PROPOSED, coverage floor chosen from measured baseline; pending maintainer review
- Date: 2026-11-01
- Milestone: M0 / E3
- Issues: PNK-M0-014 through PNK-M0-017

## Context

The E0-E2 bootstrap already passed a nine-job OS/interpreter matrix but
requires stronger failure-mode testing, reportable coverage and basic
repository supply-chain hygiene.

## Proposed decisions

1. Retain the 3 x 3 Python/OS CI matrix until updated based on execution data.
2. Use Hypothesis with deterministic examples and bounded case counts to test
   pure domain invariants, alongside exhaustive transition-table unit tests.
3. Explicitly test cancellation, timeout, pending task cleanup and bounded
   in-memory stream behavior. Do not claim these tests prove real TCP behavior.
4. Generate XML coverage and JUnit XML in every CI job, preserve them as short-
   lived artifacts, and report *branch* coverage in CI output.
5. **Enforce combined statement/branch coverage >=95%** after an observed
   baseline of **97%** (173 statements, 56 branches, three missed statements
   and three missed branches) on Python 3.11/3.13 CI environments. This floor
   leaves a small margin for platform variation and must not be lowered
   without review and a documented reason.
6. Add offline heuristic credential hygiene and `pip check` in CI, plus
   Dependabot review policy. These are complementary, not comprehensive
   supply-chain or secrets audits.
7. Keep GitHub Actions permissions least-privileged; add no release credentials.
8. Every reviewed PR should carry exact-SHA and CI run links. Previous passing
   runs cannot certify a later commit.

## Evidence

- CI: Ruff lint/format, mypy strict, property-based and async contract tests,
  branch coverage, JUnit reports, wheel/sdist build and twine.
- Test and coverage XML artifacts retained 14 days per CI run.
- Coverage enforcement is now configured using the measured baseline, not
  an arbitrary pre-implementation target. ADR still awaits owner approval.

## Trade-offs and risk

Deterministic Hypothesis cases improve reproducibility but are not a substitute
for exploratory seeded property testing and fuzzing. An offline regex-based
secret check can miss novel secrets or flag harmless examples. Upgrade it when
scope and security posture justify the additional tooling and maintenance.
