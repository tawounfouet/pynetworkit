# ADR-M1-05/06 - IPv6 capabilities and synchronous doubles

- Status: ACCEPTED for the M1 technical baseline (2026-11-02; delegated owner review)
- Date: 2026-11-02
- Issues: #37-#40, #44, #57

Reuse M0 resolved IPEndpoint: numeric IPv4/IPv6 only; do not silently
accept DNS names or scoped IPv6 identifiers. AF_INET and AF_INET6
families should be selected based on the address; test 127.0.0.1 and
::1 separately. IPv6 capability and IPV6_V6ONLY default vary across OS
images, so include capability detection and precise test skips.
Do not assert portable dual-stack, link-local interface scopes or
IPv4-mapped IPv6 conversion until those contracts are reviewed.

E00 does not introduce a full synchronous memory-network simulator.
Contract tests use small, explicit doubles for partial writes and
one-shot datagram receive behavior. E01/E02 require real bounded loopback
tests for the actual concrete adapters. This limits speculative
abstraction (KISS/YAGNI) and respects the M0 async memory contract.

## Acceptance and scope

The existing IPv4 and capability-gated IPv6 loopback suite qualifies the
chosen numeric-address-only contract across the nine CI environments.
Dual-stack auto-negotiation, scoped link-local IPv6, DNS resolution and a
full synchronous memory simulator remain explicit non-goals for M1.
Evidence: https://github.com/tawounfouet/pynetworkkit/actions/runs/41459531092.
