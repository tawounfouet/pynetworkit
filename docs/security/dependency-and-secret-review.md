# M0 E3 - Dependency and credential review policy

Status: proposed, for maintainer approval. Scope: M0 pre-alpha, no public release.

## Dependency boundaries

- The M0 runtime dependency list is intentionally empty.
- Dev extras introduce transitive dependencies through pytest, Hypothesis,
  pytest-cov, pytest-asyncio, Ruff, mypy, setuptools, build and twine.
- The CI checks `pip check` on each supported OS/Python combination.
- Dependabot is configured for weekly pull requests to inspect dependency
  version changes. Updates are reviewed and must pass the entire CI matrix.
- If available in GitHub repository settings, enable the dependency graph,
  Dependabot security alerts and private vulnerability reporting.
- Before a stable release, enable a dedicated vulnerability audit and
  review/test its findings (e.g. pip-audit or GitHub dependency review).
- Current safeguards do not claim an audit of all transitive dependencies.

## Source and credential hygiene

- CI runs an offline heuristic check against code, tests, configs and docs.
- It avoids printing token values and never contacts outside hosts.
- This is not a replacement for GitHub secret scanning, code review or
  correctly scoped security tools.
- Do not embed credentials, certificates with private keys, API tokens
  or real customer data in repository tests or documentation.
- Security validation in this phase is limited to safe, local fixtures.

## GitHub Actions safeguards

- The workflow has top-level `contents: read` permission.
- Untrusted pull requests must not receive publication credentials.
- Job secrets are not used by any M0 build.
- Workflow actions are version-tagged during M0; pin to verified commit SHAs
  as part of the release hardening policy. Review action updates separately.

## Release gate

Packaging success is not permission to publish: name, license, approvals,
supply-chain review and a reproducible release candidate are still required.
