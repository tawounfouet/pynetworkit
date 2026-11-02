# PyNetworkKit

**Python-first networking primitives, typed capability contracts, and reproducible learning labs.**

> **Pre-alpha M0/M1 development.** Source version `0.1.0a2`
> is a local development candidate only; no tag, PyPI publication
> or stable API is claimed.


## Project identity and scope

- Canonical repository: [tawounfouet/pynetworkkit](https://github.com/tawounfouet/pynetworkkit)
- Python distribution and import: `pynetworkkit`
- Development matrix: Python 3.11/3.12/3.13; Linux, macOS and Windows
- Pure network-domain types, port contracts, deterministic memory streams
- No real TCP/UDP sockets, DNS resolver, TLS or privileged probes in M0

## Install from a source checkout

```bash
git clone https://github.com/tawounfouet/pynetworkkit.git
cd pynetworkkit
python -m venv .venv
# macOS / Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python -c "import pynetworkkit; print(pynetworkkit.__version__)"
```

The source checkout can be installed without a published PyPI release.
See the [full quickstart](docs/quickstart.md).

## Three offline learning labs

```bash
python examples/lab01_ip_port.py
python examples/lab02_connection_fsm.py
python examples/lab03_memory_duplex.py
```

Learn numeric IP literals, CIDR membership, ports, IPv6 endpoint formatting,
state-machine transitions, asynchronous byte streams, EOF, full close and
resource ownership. See [learning exercises](docs/labs/README.md).

## Public API illustration

```python
from pynetworkkit.domain import IPEndpoint, Port, parse_ip_address, parse_ip_network

address = parse_ip_address("127.0.0.1")
network = parse_ip_network("127.0.0.0/8")
endpoint = IPEndpoint(address, Port(443))
assert address in network
assert str(endpoint) == "127.0.0.1:443"
```

The [API reference](docs/api/M0_PUBLIC_API.md) documents exceptions and
limitations. The memory adapter is for deterministic in-process testing, **not**
a TCP stack. Cancellation can leave a partial accepted byte prefix.

## M2 - Native Async Core (development)

The Async Core adds nonblocking TCP streams, connector/listener, UDP datagrams,
monotonic deadlines, cancellation semantics, bounded queues and structured
concurrency. The M0/M1 API remains intact. No published M2 release is implied.

See [M2 Async Public API](docs/api/M2_ASYNC_PUBLIC_API.md) and
[six offline learning labs](docs/labs/M2_ASYNC_CORE.md).

\`\`\`bash
python examples/lab_m2_01_tcp_echo.py
python examples/lab_m2_02_udp_datagram.py
python examples/lab_m2_03_cancel_deadline.py
python examples/lab_m2_04_backpressure.py
python examples/lab_m2_05_concurrent_clients.py
python examples/lab_m2_06_failures.py
\`\`\`

## Quality and build

```bash
ruff check .
ruff format --check .
mypy src/pynetworkkit
python scripts/check_repository_hygiene.py
python -m pytest -q --cov=pynetworkkit --cov-branch --cov-fail-under=95
python -m build
python -m twine check dist/*
python scripts/verify_distribution.py
```

The verifier installs the local wheel into a clean temporary virtual
environment without querying package indexes and emits a SHA256 manifest.
CI also runs the three examples in subprocesses and retains JUnit/coverage
and hash evidence for 14 days.

## Architecture, contribution and release

The five M0 epics are Repository & Packaging, Domain Kernel, Ports &
Memory Adapter, Verification & CI, and Documentation & Release.
Design is informed by DDD, SOLID/DIP/ISP, Ports & Adapters, KISS and YAGNI.

- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Architecture overview](docs/architecture.md)
- [ADR decision register](docs/adr/M0_DECISION_REGISTER.md)
- [Release checklist](RELEASE_CHECKLIST.md)
- [Candidate GO/NO-GO gate](docs/releases/M0_ALPHA_RELEASE_READINESS.md)
- [M0 technical closure and evidence](docs/releases/M0_TECHNICAL_CLOSURE_2026-11-01.md)
- [Changelog](CHANGELOG.md)

**License: [MIT](LICENSE)**, copyright (c) 2026 Thomas AWOUNFOUET.
Preserve the copyright and MIT permission notice in copies and substantial
portions of the software. Publication of `0.1.0a1` still requires code reviews,
protected branch checks, ADR approvals and explicit release authorization.

## M1 Socket Kernel - development branch

The M1 implementation adds synchronous TCP and UDP adapter capabilities.
See [M1 quickstart](docs/quickstart_m1.md), the
[M1 labs](docs/labs/M1_SOCKET_KERNEL.md), and
[ADR-M1-01](docs/adr/0005-m1-sync-ports-and-partial-io.md).
Blocking socket operations remain separate from M0 async memory ports.

This section describes development work only; the M0 alpha release
governance issue [#29](https://github.com/tawounfouet/pynetworkkit/issues/29)
remains an independent publication gate. No tag or PyPI release is
implied by the presence of M1 code.
