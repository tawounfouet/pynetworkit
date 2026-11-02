"""Execute the shipped offline learning labs in the CI matrix."""

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("lab01_ip_port.py", "lab01: IPv4 CIDR, Port, IPv6 endpoint OK"),
        ("lab02_connection_fsm.py", "lab02: lifecycle and rejected transition OK"),
        ("lab03_memory_duplex.py", "lab03: bidirectional bytes, partial reads and EOF OK"),
        ("lab_m1_01_tcp_echo.py", "lab_m1_01: TCP echo, partial I/O, EOF and teardown OK"),
        ("lab_m1_02_udp_datagram.py", "lab_m1_02: UDP source, empty payload and truncation OK"),
        ("lab_m1_03_fault_investigations.py", "lab_m1_03: timeout, TCP EOF and closed UDP channel OK"),
    ],
)
def test_offline_learning_lab(filename: str, expected: str) -> None:
    """A fresh user can execute each lab after installing the project."""
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "examples" / filename)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    assert result.stdout.strip() == expected
    assert result.stderr == ""
