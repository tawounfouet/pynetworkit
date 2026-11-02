# PyNetworkKit 0.2.0a1 - Publication gate (G6)

**Date:** 2026-11-02
**Technical status:** M2 candidate qualified, pending final closure PR check.
**Publication verdict:** **NO-GO - not approved**.

The passing audit [41525452563](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525452563)
validates a local wheel and sdist, SHA256 hashes, vulnerability scan of
auditable development dependencies and 240 passing tests. The locally
installed unpublished PyNetworkKit distribution was skipped by pip-audit
because it does not exist on PyPI; this is not a finding of zero package bugs.

**Not performed:** Git tag, GitHub Release, TestPyPI/PyPI publication,
OIDC publishing action, name registry reservation or irreversible promotion.

To request G6 GO, collect explicit publication authorisation, confirm the
registry owner/name, verify artifact retention and checksums, review release
notes/API compatibility, run separate security and dependency audit against
the exact approved final SHA, and document rollback and provenance. Preserve
the independent M0/M1 candidate and release issues #29/#67.

A successful merge on main does not implicitly satisfy any of those approvals.
