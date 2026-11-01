"""Fast, offline, heuristic checks for accidentally committed credentials.

This check is deliberately narrow: a PASS is not a professional secret scan.
It never prints matched credential contents. No network calls are made.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = frozenset({".py", ".toml", ".md", ".yaml", ".yml"})
SEARCH_DIRS = ("src", "tests", "docs", ".github")
ROOT_FILES = ("README.md", "SECURITY.md", "pyproject.toml", "CONTRIBUTING.md")
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "credential assignment",
        re.compile(
            r"""(?i)\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*['\"][^'\"
]{8,}['\"]"""
        ),
    ),
    (
        "token prefix",
        re.compile(r"(?:ghp_|github_pat_)[A-Za-z0-9_]{30,}"),
    ),
    (
        "private key header",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
)


def source_files() -> list[Path]:
    """Enumerate source/configuration files without consulting the Internet."""
    found = [ROOT / filename for filename in ROOT_FILES if (ROOT / filename).is_file()]
    for dirname in SEARCH_DIRS:
        folder = ROOT / dirname
        if folder.is_dir():
            found.extend(
                path
                for path in folder.rglob("*")
                if path.is_file() and not path.is_symlink() and path.suffix in SUFFIXES
            )
    return sorted(found)


def main() -> int:
    """Return a failing exit code if likely credential material was found."""
    findings: list[str] = []
    for path in source_files():
        relative = path.relative_to(ROOT)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for label, expression in PATTERNS:
                if expression.search(line):
                    findings.append(f"{relative}:{number}: {label}")
    if findings:
        print("Potential credential material detected (values deliberately hidden):")
        print("\n".join(findings))
        return 1
    print(f"Repository hygiene check passed ({len(source_files())} text files inspected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
