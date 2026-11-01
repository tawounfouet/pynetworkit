# ADR-0001: Python baseline, packaging and project naming

- Status: **proposed**, naming and MIT licensing choices confirmed on 2026-11-01; other decisions remain under review
- Milestone: M0 E0
- Date: 2026-10-31

## Context

PyNetworkKit aims to expose a typed, reusable Python package with no runtime
third-party dependencies in its initial kernel. The public GitHub repository was initially named `pynetworkit`, but the maintainer
renamed it to `pynetworkkit` on 2026-11-01. The repository, planned distribution
and Python import name now all use `pynetworkkit`.

## Proposed decisions

1. Target Python `>=3.11`; verify each claimed OS and interpreter in CI.
2. Use `src/` layout, PEP 621 metadata, PEP 561 `py.typed` and setuptools.
3. Keep runtime dependencies empty for M0.
4. Use `pynetworkkit.__version__` as the single dynamic version source.
5. **Naming decision confirmed:** use `pynetworkkit` consistently for the GitHub
   repository, the Python distribution and the import. The historical typo
   `pynetworkit` must not appear in canonical links or new setup commands.
6. **License decision confirmed:** MIT with copyright (c) 2026 Thomas AWOUNFOUET.
   Commit root LICENSE; use PEP 639 SPDX `license = "MIT"` and
   `license-files = ["LICENSE"]` in pyproject.toml. Require setuptools>=77.0.3
   to support these fields. Publication and naming availability reviews remain separate.
7. Prefer smaller domain/ports/adapters modules rather than forcing OSI layers
   into Python package paths.

## Alternatives considered

- Hatchling: valid PEP 517 alternative, but introduces another build tool.
- Static version duplicated in `pyproject.toml`: easier initially, but drifts.
- Python 3.12+ only: simplifies some typing features but limits audience.

## Consequences and verification

- Confirm `pip install -e '.[dev]'`, imports and clean wheel/sdist installations.
- CI must verify Python 3.11/3.12/3.13 on intended OS environments.
- The repository naming decision is resolved and GitHub confirms the new slug.
- The MIT license choice is confirmed by the maintainer; the ADR as a whole
  remains proposed until other technical decisions are accepted.
- Record the precise SHA and results before upgrading this ADR to accepted.
