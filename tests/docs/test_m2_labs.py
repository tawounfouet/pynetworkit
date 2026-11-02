"""Execute the M2 teaching labs from a source checkout, offline."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "filename",
    [
        "lab_m2_01_tcp_echo.py",
        "lab_m2_02_udp_datagram.py",
        "lab_m2_03_cancel_deadline.py",
        "lab_m2_04_backpressure.py",
        "lab_m2_05_concurrent_clients.py",
        "lab_m2_06_failures.py",
    ],
)
def test_m2_lab_is_executable(filename: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "examples" / filename)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    assert result.stdout.strip()
    assert not result.stderr
