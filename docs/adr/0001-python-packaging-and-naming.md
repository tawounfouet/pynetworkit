# ADR-0001: Python baseline, packaging and project naming

- Status: **proposed**, pending maintainer review and CI evidence
- Milestone: M0 E0
- Date: 2026-10-31

## Context

PyNetworkKit aims to expose a typed, reusable Python package with no runtime
third-party dependencies in its initial kernel. The existing public GitHub
repository is named `pynetworkit`, while the intended distribution and Python
import name in the design documents is `pynetworkkit`.

## Proposed decisions

1. Target Python `>=3.11`; verify each claimed OS and interpreter in CI.
2. Use `src/` layout, PEP 621 metadata, PEP 561 `py.typed` and setuptools.
3. Keep runtime dependencies empty for M0.
4. Use `pynetworkkit.__version__` as the single dynamic version source.
5. Retain the existing repository slug until the maintainer decides whether to
   rename it; this must not silently change the distribution name.
6. Defer choosing a license. Do not publish to PyPI or assert open-source rights
   before an explicit license decision and name-availability check.
7. Prefer smaller domain/ports/adapters modules rather than forcing OSI layers
   into Python package paths.

## Alternatives considered

- Hatchling: valid PEP 517 alternative, but introduces another build tool.
- Static version duplicated in `pyproject.toml`: easier initially, but drifts.
- Python 3.12+ only: simplifies some typing features but limits audience.

## Consequences and verification

- Confirm `pip install -e '.[dev]'`, imports and clean wheel/sdist installations.
- CI must verify Python 3.11/3.12/3.13 on intended OS environments.
- License and repository naming remain **open decisions**, not accepted facts.
- Record the precise SHA and results before upgrading this ADR to accepted.
