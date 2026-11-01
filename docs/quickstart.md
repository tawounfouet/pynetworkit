# PyNetworkKit quickstart - M0 (pre-alpha)

## Goals

In this guide you will parse IPv4/IPv6 numeric literals, validate a Port,
check a CIDR network, follow a connection lifecycle and communicate over a
bounded **in-memory** duplex stream. None of these examples contacts a host,
runs DNS resolution, or opens a network socket.

## Supported development matrix

Python 3.11, 3.12 and 3.13 on Linux, macOS and Windows were validated in
the stacked E3 CI on GitHub. This does **not** imply broader support for
production networking, nor a published stable release.

## Install from a checkout

```bash
git clone https://github.com/tawounfouet/pynetworkkit.git
cd pynetworkkit
python -m venv .venv
```

On macOS/Linux: `source .venv/bin/activate`.
On Windows PowerShell: `.venv\Scripts\Activate.ps1`.

**Important:** until the M0 stacked PRs are merged, checkout the E4 branch:

```bash
git checkout feat/m0-e4-documentation-release
python -m pip install -e '.[dev]'
python -c "import pynetworkkit; print(pynetworkkit.__version__)"
```

The version string `0.1.0a1` is a development target, not proof of a
published package on PyPI.

## Run the three labs

```bash
python examples/lab01_ip_port.py
python examples/lab02_connection_fsm.py
python examples/lab03_memory_duplex.py
```

Expected output:

```text
lab01: IPv4 CIDR, Port, IPv6 endpoint OK
lab02: lifecycle and rejected transition OK
lab03: bidirectional bytes, partial reads and EOF OK
```

Exercises and discussion prompts are in [the labs guide](labs/README.md).
The exact scripts are also executed as subprocesses by
`tests/docs/test_learning_labs.py` on every CI platform.

## Run quality checks

```bash
ruff check .
ruff format --check .
mypy src/pynetworkkit
python -m pytest -q --cov=pynetworkkit --cov-branch --cov-fail-under=95
python scripts/check_repository_hygiene.py
python -m build
python -m twine check dist/*
python scripts/verify_distribution.py
```

The last command installs the built wheel into a fresh isolated virtual
environment **without PyPI access**. See
[release readiness](releases/M0_ALPHA_RELEASE_READINESS.md).

## Public contract, guarantees and limitations

See [the M0 API reference](api/M0_PUBLIC_API.md). Key constraints:

- `IPAddress` and `IPNetwork` are standard-library type aliases.
- CIDR parsing is strict by default. `Port(0)` is valid for ephemeral binds.
- `IPEndpoint` only accepts numeric IP addresses, not DNS names.
- `read(n)` yields **at most n bytes**, and `b""` means EOF after buffered
  bytes are consumed. There are no message boundaries.
- `write(data)` may accept a prefix of a payload before cancellation. A
  successful write means accepted by the stream, not processed by the peer.
- `aclose()` is full local close and idempotent. Half-close is not exposed.
- The memory adapter is a deterministic test double, not TCP, UDP, TLS,
  routing, an OS socket, or a network simulator.
- The API may change before the first stable release.

PyNetworkKit uses the [MIT License](../LICENSE), copyright (c) 2026
Thomas AWOUNFOUET. Copies and substantial portions must preserve the MIT
copyright and permission notice.
