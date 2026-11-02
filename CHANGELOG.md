# Changelog

All notable changes will be recorded in this file. Versions follow PEP 440.

## Unreleased

### M2 Async Core - source candidate `0.2.0a1` (unpublished)

- Native `asyncio` TCP stream, connector and pull-based listener; nonblocking
  accept, explicit stream ownership, bounded write chunks and `drain`.
- Native `asyncio` UDP channel with sender metadata, empty datagrams,
  portable truncation indication and IPv4/IPv6 capability-gated tests.
- Monotonic absolute deadlines, cooperative cancellation semantics,
  byte/item-bounded queues and task-bounded structured concurrency.
- Shared M0/M2 contract tests and six offline M2 learning labs.
- No HTTP, TLS, DNS implementation or publishing authorization in M2.


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
> The `0.1.0a2` M1 source candidate remains historically qualified at its
> original commit and artifacts; M2 source `0.2.0a1` does not retroactively
> publish or replace those artifacts.
