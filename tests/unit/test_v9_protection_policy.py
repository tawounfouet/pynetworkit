"""Regression tests for the V9 GitHub REST branch protection request payload.

Runs only the embedded Python payload builder using synthetic check-runs.
No GitHub access, write action, or system gh authentication is needed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/github/v9_main_protection.sh"


def _generator() -> str:
    source = SCRIPT.read_text(encoding="utf-8")
    marker = """python3 - "$TMP/checks.json" "$TMP/rulesets.json" "$TMP/policy.json" <<'PY'\n"""
    assert source.count(marker) == 1
    return source.split(marker, 1)[1].split("\nPY\n", 1)[0]


def _run_generator(
    tmp_path: Path,
    *,
    rulesets: list[dict[str, str]] | None = None,
    bad_check: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], Path]:
    checks = [
        {
            "name": f"Quality / {os} / Python {py}",
            "conclusion": "failure" if f"{os}/{py}" == bad_check else "success",
            "app": {"id": 15368},
        }
        for os in ("ubuntu-latest", "macos-latest", "windows-latest")
        for py in ("3.11", "3.12", "3.13")
    ]
    checks_file = tmp_path / "checks.json"
    rules_file = tmp_path / "rulesets.json"
    policy_file = tmp_path / "policy.json"
    checks_file.write_text(json.dumps({"check_runs": checks}), encoding="utf-8")
    rules_file.write_text(json.dumps(rulesets or []), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            _generator(),
            str(checks_file),
            str(rules_file),
            str(policy_file),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    return result, policy_file


def test_v9_payload_uses_checks_without_contexts(tmp_path: Path) -> None:
    completed, path = _run_generator(tmp_path)
    assert completed.returncode == 0, completed.stderr
    policy = json.loads(path.read_text(encoding="utf-8"))
    required = policy["required_status_checks"]
    assert required["strict"] is True
    assert "checks" in required
    assert "contexts" not in required
    assert len(required["checks"]) == 9
    assert len({entry["context"] for entry in required["checks"]}) == 9
    assert {entry["app_id"] for entry in required["checks"]} == {15368}
    assert policy["required_pull_request_reviews"]["required_approving_review_count"] == 0
    assert policy["enforce_admins"] is True
    assert policy["required_conversation_resolution"] is True
    assert policy["required_linear_history"] is True
    assert policy["allow_force_pushes"] is False
    assert policy["allow_deletions"] is False


@pytest.mark.parametrize("bad_check", ["ubuntu-latest/3.11", "windows-latest/3.13"])
def test_v9_payload_refuses_failing_check(tmp_path: Path, bad_check: str) -> None:
    completed, path = _run_generator(tmp_path, bad_check=bad_check)
    assert completed.returncode != 0
    assert not path.exists()


def test_v9_payload_refuses_existing_ruleset(tmp_path: Path) -> None:
    completed, path = _run_generator(tmp_path, rulesets=[{"name": "existing"}])
    assert completed.returncode != 0
    assert not path.exists()
