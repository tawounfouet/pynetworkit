# PyNetworkKit M1 Socket Kernel quickstart

Status: development candidate. This page does not authorize tagging,
GitHub Releases or PyPI publication.

## Setup

```bash
git clone https://github.com/tawounfouet/pynetworkkit.git
cd pynetworkkit
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
```

## Run M1 labs

```bash
python examples/lab_m1_01_tcp_echo.py
python examples/lab_m1_02_udp_datagram.py
python examples/lab_m1_03_fault_investigations.py
```

M1 adds four independent synchronous Protocol capabilities and concrete
TCP/UDP socket adapters under `pynetworkkit.adapters.socket`.

```python
from pynetworkkit.adapters.socket import SocketTCPListener, SocketTCPConnector
from pynetworkkit.domain import IPEndpoint

with SocketTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0)) as server:
    with SocketTCPConnector().connect(server.local_endpoint, timeout=2) as client:
        accepted, remote = server.accept(timeout=2)
        with accepted:
            client.write(b"hello", timeout=2)
            assert accepted.read(5, timeout=2) == b"hello"
```

- A successful TCP `write` can return a partial byte count; loop if
  required. Use `read` repeatedly until all application bytes arrive.
- `read(...)` returning `b""` is TCP EOF; UDP `b""` is legitimate data.
- UDP `ReceivedDatagram.truncated` is an explicit flag, and consumed
  oversized datagrams cannot be resumed.
- No DNS, TLS, multihoming negotiation or privileged external traffic.
- Timeout `None` means normal blocking behavior, potentially indefinite.
  Production callers should select finite timeouts.
- Do not share a single socket between independent owners or concurrently
  mutate its timeout. Thread safety is not promised in M1.
- `Port(0)` is valid for local bind, invalid for remote TCP connect.

## Qualification

```bash
ruff check .
ruff format --check .
mypy src/pynetworkkit
python -m pytest -q --cov=pynetworkkit --cov-branch --cov-fail-under=95
python -m build
python -m twine check dist/*
python scripts/verify_distribution.py
```

CI runs this on Python 3.11/3.12/3.13 across Linux/macOS/Windows.
A passing test does not approve an ADR or authorize publication.
