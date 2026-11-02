"""Guard the patched build-tool floor and the blocking candidate audit gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_build_backend_requires_patched_setuptools() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "setuptools>=84.1.0" in project["build-system"]["requires"]


def test_candidate_installs_patched_setuptools_before_auditing() -> None:
    workflow = (ROOT / ".github/workflows/release-candidate.yml").read_text(encoding="utf-8")
    upgrade = workflow.index("python -m pip install --upgrade 'setuptools>=84.1.0'")
    editable = workflow.index("python -m pip install -e '.[dev]'")
    audit = workflow.index("run: pip-audit --local")
    assert upgrade < editable < audit
    assert "run: pip-audit --local || true" not in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "id-token: write" not in workflow
