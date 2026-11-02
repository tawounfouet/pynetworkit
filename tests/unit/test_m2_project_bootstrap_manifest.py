"""Validate the versioned M2 Project v2 bootstrap without contacting GitHub."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "scripts/github/m2_backlog_manifest.json"
SCRIPT = ROOT / "scripts/github/m2_project_bootstrap.sh"
PLAN = ROOT / "docs/roadmap/29_PYNETWORKKIT_M2_ASYNC_CORE_IMPLEMENTATION_PLAN.md"
GUIDE = ROOT / "docs/roadmap/30_PYNETWORKKIT_M2_GITHUB_PROJECT_V2_INTEGRATION_AND_BOOTSTRAP.md"


def test_manifest_has_all_42_unique_keys_and_six_groups() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["repository"] == "tawounfouet/pynetworkkit"
    assert manifest["project_number"] == 9
    assert manifest["project_id"] == "PVT_kwHOBKwz2s4Bpywv"
    assert manifest["milestone_title"] == "M2 - Async Core (v0.2.0a1)"
    assert manifest["plan_path"] == str(PLAN.relative_to(ROOT))
    epics, tasks = manifest["epics"], manifest["tasks"]
    assert len(epics) == 6 and len(tasks) == 36
    keys = [e["id"] for e in epics] + [t["id"] for t in tasks]
    assert len(set(keys)) == 42
    assert [int(t["id"][-3:]) for t in tasks] == list(range(1, 37))
    assert {t["priority"] for t in tasks} == {"P0", "P1"}
    assert {t["issue_number"] for t in tasks} == set(range(79, 115))
    for epic in epics:
        children = [t["id"] for t in tasks if t["epic"] == epic["id"]]
        assert children == epic["tasks"]
        assert len(children) == 6


def test_shell_wrapper_embedded_python_compiles_without_running() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    tag = "PYNETWORKKIT_M2_BOOTSTRAP_PYTHON"
    assert source.count("<<'" + tag + "'") == 1
    python_source = source.split("<<'" + tag + "'\n", 1)[1].rsplit("\n" + tag, 1)[0]
    compile(python_source, str(SCRIPT), "exec")


def test_bootstrap_is_preview_by_default_and_preserves_release_gates() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'exec python3 - "$@"' in source
    assert 'g.add_argument("--apply", action="store_true"' in source
    assert 'g.add_argument("--verify", action="store_true"' in source
    assert "if args.apply:" in source
    assert "PREVIEW ONLY - no GitHub mutations" in source
    assert "No automatic tag, Release, TestPyPI or PyPI publication." in source
    assert "replace_parent" not in source
    assert "gh auth" not in source or "gh auth login" in source


def test_plan_links_catalog_to_actual_issues_and_release_gates() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    guide = GUIDE.read_text(encoding="utf-8")
    assert "## 7. Backlog" in plan
    assert "PNK-M2-001" in plan and "PNK-M2-036" in plan
    assert "issues/79" in plan and "issues/114" in plan
    assert "NO-GO" in plan
    assert "42 issues" in guide
    assert "main" in guide and "Project" in guide
