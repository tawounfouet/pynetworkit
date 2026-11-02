# PyNetworkKit M2 - Implementation evidence ledger

Date: 2026-11-02. Scope: source implementation and technical qualification only.

This ledger records **verified PR CI runs and merged SHA evidence**, not
the claim that a PyPI release was authorized or published.

## Technical PR evidence

| Pull request | PR head SHA tested | main merge SHA | GitHub Actions run | Scope |
| --- | --- | --- | --- | --- |
| [#116](https://github.com/tawounfouet/pynetworkkit/pull/116) | `8b90873078722e3781376d7f5da1a596d461d5bd` | `d15edab7b5906aee38774b33c012f2d61261245c` | [41520941936](https://github.com/tawounfouet/pynetworkkit/actions/runs/41520941936) (9/9 quality) | E00 - async contracts and ADR proposals |
| [#117](https://github.com/tawounfouet/pynetworkkit/pull/117) | `ada04a42c64772c85f7eb3a180e71dcac77dde95` | `4af0388f6128f989f7d9ed0d7e3dd5a053c2e983` | [41521309028](https://github.com/tawounfouet/pynetworkkit/actions/runs/41521309028) (9/9 quality) | E01 - asyncio TCP streams/connector/listener |
| [#118](https://github.com/tawounfouet/pynetworkkit/pull/118) | `bb0b101579340840fa2142d178a3991a25719cb6` | `d49495626278e89cf6a7efdcc09f9a90b0d047d8` | [41521746544](https://github.com/tawounfouet/pynetworkkit/actions/runs/41521746544) (9/9 quality) | E02 - asyncio UDP and datagram semantics |
| [#119](https://github.com/tawounfouet/pynetworkkit/pull/119) | `15318959c8d4ea14c5cc7761067487e5bb48f3d7` | `0337ea7cb526ac64776846ca96d2aafc5b39036f` | [41522208657](https://github.com/tawounfouet/pynetworkkit/actions/runs/41522208657) (9/9 quality) | E03 - cancellation and monotonic deadline |
| [#120](https://github.com/tawounfouet/pynetworkkit/pull/120) | `e95dadcf7d37ab9b581d1eb530fef1d9e6589eb8` | `e2e200bb9420e5cf8dede6581f523e717fd10764` | [41523041908](https://github.com/tawounfouet/pynetworkkit/actions/runs/41523041908) (9/9 quality) | E04 - backpressure and task caps |
| [#121](https://github.com/tawounfouet/pynetworkkit/pull/121) | `35d96115f9be2babec2e2e240f6724f72dd7dce6` | `188ebe86375fcce31d21bb7c32a0de32a3754db8` | [41523551973](https://github.com/tawounfouet/pynetworkkit/actions/runs/41523551973) (9/9 quality) | E05 - contracts, six labs and IPv6 |

## Baseline and forward-only versions

- The M0/M1 source and user-facing API are retained. The M1 candidate
  `0.1.0a2` was independently audited at
  [M1 audit 41494741435](https://github.com/tawounfouet/pynetworkkit/actions/runs/41494741435)
  with 190 tests, 98.90% coverage, and an unpublished wheel/sdist.
- A new M2 `0.2.0a1` *source development candidate* does not replace,
  retag or publish the earlier M1 SHA or artifacts.
- The M2 release candidate and artifact checksums must be audited on
  the final main commit before a technical closure verdict.

## Contract and transport evidence

- `tests/unit/test_m2_port_shapes.py` preserves M0/M1 public names.
- `tests/contracts/test_m2_async_stream_contracts.py` runs the same byte
  stream contract on M0 memory and M2 TCP adapters.
- `tests/contracts/test_m2_async_datagram_contracts.py` tests sender
  identity, empty datagrams, boundaries and truncation.
- `tests/integration/test_m2_ipv6.py` gates IPv6 by OS capability.
- Cancellation tests include read/recv/accept and injected connect,
  partial write and interrupted close in the qualification hardening PR.
- `tests/unit/test_m2_bounded_queue.py` and bounded_map tests prove
  finite capacity, cancellation cleanup and constrained worker count.

## Pending qualification

- M2 security candidate audit result, exact main SHA, wheel/sdist hashes
  and any errors found in pip-audit.
- Final 9/9 CI on the closure main SHA.
- Verified issue closure and GitHub Project view/field reconciliation.
- M2 technical closure and independent publication gate.

No artifacts were published by this ledger.
