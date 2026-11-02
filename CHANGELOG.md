# Changelog

All notable changes will be recorded in this file. Versions follow PEP 440.

## Unreleased

### Added

- M1 sync Protocol ports for TCP stream/connector/listener and UDP datagram.
- Concrete OS socket adapters with exclusive ownership, per-operation
  timeouts, EOF and half-close, bounded UDP truncation observability.
- Real IPv4/IPv6 capability-gated loopback and fault-injection tests.
- M1 TCP echo, UDP datagram and fault investigation learning labs.
- M1 API reference, ADR proposals and qualification ledger.

- M0 E0 repository bootstrap, packaging metadata and project quality tooling.
- M0 E1 pure addressing value objects and connection lifecycle model.
- M0 E2 bounded in-memory duplex streams and reusable async contracts.
- M0 E3 deterministic property tests, cancellation and timeout verification,
  combined coverage gate (95%), test evidence artifacts and security hygiene.
- M0 E4 executable offline quickstart labs, API and ADR review ledger,
  clean isolated wheel verification and SHA256 candidate evidence.
- MIT licensing with SPDX PEP 639 metadata and bundled license notice.

> `0.1.0a1` was a technical M0 candidate and remains unpublished.
> The `0.1.0a2` source version identifies M1 development, not a
> tagged or published release.
