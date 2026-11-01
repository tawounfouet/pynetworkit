# Contributing to PyNetworkKit

Development is organized as small, reviewable increments aligned with M0 issues
`PNK-M0-001` through `PNK-M0-020`.

1. Start from `main` and create a feature branch named `feat/m0-<epic>-<topic>`.
2. Include the issue ID and a narrowly defined result in the pull request.
3. Record the network concept, the Python mechanism, design principle, trade-off
   and acceptance evidence for nontrivial changes (Software Design & Learning).
4. Run `ruff check .`, `ruff format --check .`, `mypy src/pynetworkkit`,
   `pytest -q` and `python -m build` locally when dependencies are available.
5. Do not merge when required checks fail, or claim a platform is supported
   without CI evidence. No force pushes to `main`.

## Architecture boundaries

- Domain models must not import `socket`, `asyncio` or external infrastructure.
- `ports/` defines contracts; `adapters/` implements them.
- Network tests use controlled memory transports or localhost, never third-party
  infrastructure by default.
- Preserve explicit semantics for EOF, close, timeout, cancellation and ownership.
- New abstractions require a concrete use case (KISS/YAGNI).

See the [security policy](SECURITY.md) for reporting guidance.
