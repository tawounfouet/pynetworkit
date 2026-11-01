# PyNetworkKit

**Python-first networking primitives and composable transport contracts.**

> Status: **pre-alpha (M0 bootstrap)**. This is an educational and engineering toolkit,
> not a replacement for the operating system's TCP/IP implementation.

## Identity and scope

- GitHub repository: [`tawounfouet/pynetworkkit`](https://github.com/tawounfouet/pynetworkkit)
- Python distribution and import name: `pynetworkkit`
- Planned alpha version: `0.1.0a1`
- Python policy: `>=3.11`, pending CI evidence across supported environments

**Naming resolved:** the GitHub repository, Python distribution and import are now
consistently named `pynetworkkit`. See [ADR-0001](docs/adr/0001-python-packaging-and-naming.md).

## Local bootstrap

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python -c 'import pynetworkkit; print(pynetworkkit.__version__)'
ruff check .
ruff format --check .
mypy src/pynetworkkit
pytest -q
python -m build
python -m twine check dist/*
```

The package currently exposes only its version. Domain value objects and in-memory
transports are planned for subsequent M0 epics; no live TCP/UDP socket support is
claimed before M1.

## Architecture and delivery

M0 has five epics: E0 Repository & Packaging, E1 Domain Kernel, E2 Ports & Memory,
E3 Verification & CI, and E4 Documentation & Release. Production TCP/UDP adapters
belong to M1. The architecture follows domain purity, capability-specific ports,
replaceable adapters, explicit lifecycle rules and reproducible tests.

Read [the contributor guide](CONTRIBUTING.md) and [security policy](SECURITY.md).

## License and releases

PyNetworkKit is licensed under the [MIT License](LICENSE), copyright (c) 2026
Thomas AWOUNFOUET. Preserve the copyright and license notice in substantial
copies or distributions. MIT provides the software without warranty.
No PyPI release or verified GitHub release exists yet. Publication still needs
security and quality review, the complete M0 integration and explicit approval.
