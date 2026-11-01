"""Verify an M0 wheel in a clean offline venv and hash candidate artifacts.

Requires one local dist/*.whl and one local dist/*.tar.gz. Never uses PyPI
or publishes. Designed to run on Linux, macOS and Windows.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MANIFEST = ROOT / "release-evidence" / "SHA256SUMS.txt"


def run_command(*args: str) -> None:
    """Run one bounded subprocess without a shell."""
    subprocess.run(args, check=True, cwd=ROOT, timeout=120)


def checksum(path: Path) -> str:
    """Compute an artifact's SHA256 digest without loading it all into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    """Check package content, isolated install, imports and artifact SHA256."""
    wheels = sorted(DIST.glob("pynetworkkit-*.whl"))
    sdists = sorted(DIST.glob("pynetworkkit-*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit("Expected exactly one PyNetworkKit wheel and one sdist in dist/")

    wheel, sdist = wheels[0], sdists[0]
    with ZipFile(wheel) as archive:
        members = set(archive.namelist())
        required = {
            "pynetworkkit/py.typed",
            "pynetworkkit/domain/addressing.py",
            "pynetworkkit/adapters/memory/streams.py",
        }
        if missing := required - members:
            raise SystemExit(f"Wheel is missing required package members: {sorted(missing)}")
        metadata_files = [name for name in members if name.endswith(".dist-info/METADATA")]
        license_files = [name for name in members if name.endswith(".dist-info/licenses/LICENSE")]
        if len(metadata_files) != 1 or len(license_files) != 1:
            raise SystemExit("Wheel must contain PEP 639 metadata and MIT LICENSE")
        wheel_metadata = archive.read(metadata_files[0]).decode("utf-8")
        if "License-Expression: MIT" not in wheel_metadata:
            raise SystemExit("Wheel metadata does not declare SPDX License-Expression: MIT")
        if "License-File: LICENSE" not in wheel_metadata:
            raise SystemExit("Wheel metadata does not declare License-File: LICENSE")

    with tempfile.TemporaryDirectory(prefix="pynetworkkit-wheel-") as temporary:
        target = Path(temporary) / "environment"
        venv.EnvBuilder(with_pip=True).create(target)
        interpreter = (
            target / "Scripts" / "python.exe"
            if sys.platform == "win32"
            else target / "bin" / "python"
        )
        run_command(
            str(interpreter),
            "-m",
            "pip",
            "--disable-pip-version-check",
            "install",
            "--no-index",
            "--no-deps",
            str(wheel.resolve()),
        )
        run_command(
            str(interpreter),
            "-c",
            (
                "from importlib.metadata import metadata, version;"
                "import pynetworkkit;"
                "from pynetworkkit.domain import Port, IPEndpoint;"
                "from pynetworkkit.adapters.memory import create_memory_stream_pair;"
                "assert pynetworkkit.__version__ == version('pynetworkkit');"
                "assert str(Port(443)) == '443';"
                "assert str(IPEndpoint.parse('::1', 443)) == '[::1]:443';"
                "assert callable(create_memory_stream_pair);"
                "assert metadata('pynetworkkit')['License-Expression'] == 'MIT'"
            ),
        )
        run_command(str(interpreter), "-m", "pip", "check")

    manifest_lines = [f"{checksum(artifact)}  {artifact.name}" for artifact in (wheel, sdist)]
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print("Isolated wheel import, metadata and offline dependency verification: PASS")
    print("Local SHA256 manifest:", MANIFEST.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
