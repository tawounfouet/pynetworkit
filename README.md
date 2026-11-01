# PyNetworkKit

**Python-first networking primitives, typed capability contracts, and reproducible learning labs.**

> **Pre-alpha M0 development branch.** The version string `0.1.0a1`
> is planned; no public release, PyPI publication or stable API is claimed.
> The M0 E0-E4 pull requests are stacked and not merged into `main`.

## Project identity and scope

- Canonical repository: [tawounfouet/pynetworkkit](https://github.com/tawounfouet/pynetworkkit)
- Python distribution and import: `pynetworkkit`
- Development matrix: Python 3.11/3.12/3.13; Linux, macOS and Windows
- Pure network-domain types, port contracts, deterministic memory streams
- No real TCP/UDP sockets, DNS resolver, TLS or privileged probes in M0

## Install from the E4 working branch

```bash
git clone https://github.com/tawounfouet/pynetworkkit.git
cd pynetworkkit
git checkout feat/m0-e4-documentation-release
python -m venv .venv
# macOS / Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python -c "import pynetworkkit; print(pynetworkkit.__version__)"
```

A fresh checkout of `main` does **not** yet include these changes.
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
- [Changelog](CHANGELOG.md)

**No license has been selected.** Public repository visibility does not
automatically grant reuse rights. Do not tag, announce or publish until the
license, code reviews, protected branch checks, ADRs and release approval
are explicitly completed.
