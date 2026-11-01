"""Guard dependency inversion: domain and ports cannot import OS networking."""

import ast
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src" / "pynetworkkit"
FORBIDDEN_MODULES = frozenset(
    {
        "asyncio",
        "socket",
        "ssl",
        "selectors",
        "subprocess",
        "pynetworkkit.adapters",
        "pynetworkkit.application",
    }
)


def test_domain_and_ports_are_infrastructure_independent() -> None:
    for package in ("domain", "ports"):
        modules = list((SOURCE_ROOT / package).rglob("*.py"))
        assert modules, f"Missing expected Python package: {package}"
        for path in modules:
            syntax = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports: list[str] = []
            for node in ast.walk(syntax):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
            for name in imports:
                assert all(
                    name != forbidden and not name.startswith(f"{forbidden}.")
                    for forbidden in FORBIDDEN_MODULES
                ), f"{path.relative_to(SOURCE_ROOT)} imports forbidden dependency {name}"
