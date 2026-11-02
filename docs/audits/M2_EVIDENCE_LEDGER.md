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
| [#122](https://github.com/tawounfouet/pynetworkkit/pull/122) | `2825976979469800d4efc01cf20d5a38a4ae1a91` | `54b9a18a27af4b22b66d2ab25c600f77c8a9b3c6` | [41524396285](https://github.com/tawounfouet/pynetworkkit/actions/runs/41524396285) (9/9 quality) | Cancellation injection, M2 source `0.2.0a1` |
| [#123](https://github.com/tawounfouet/pynetworkkit/pull/123) | `6e02890983635ff9842ca8a4dd7c678b78d44720` | `d29d686a5fb01c8d5161e1a5fe6051967dfa0d12` | [41525150933](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525150933) (9/9 quality) | ADRs accepted, evidence ledger, audit candidate workflow |

## Baseline and forward-only versions

- The M0/M1 source and user-facing API are retained. The M1 candidate
  `0.1.0a2` was independently audited at
  [M1 audit 41494741435](https://github.com/tawounfouet/pynetworkkit/actions/runs/41494741435)
  with 190 tests, 98.90% coverage, and an unpublished wheel/sdist.
- A new M2 `0.2.0a1` *source development candidate* does not replace,
  retag or publish the earlier M1 SHA or artifacts.
- The M2 source candidate was audited on main SHA
  `d29d686a5fb01c8d5161e1a5fe6051967dfa0d12`; the exact final
  closure SHA will be verified separately after the report PR merges.

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

## M2 candidate qualification at main SHA

- Verified main SHA: `d29d686a5fb01c8d5161e1a5fe6051967dfa0d12`.
- [Main CI run 41525452114](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525452114): **9/9 success**.
- [M2 candidate security run 41525452563](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525452563): **success**, 240 tests, **97.54%** branch coverage.
- `pip-audit --local`: no known vulnerabilities in auditable installed dependencies. The unpublished local `pynetworkkit==0.2.0a1` distribution is explicitly **skipped** as unavailable on PyPI, not certified as externally audited.
- Wheel and sdist built; `twine check` passed; clean isolated wheel install, imports and metadata passed; SHA256 manifest verified both files as OK.
- Candidate artifact: [GitHub Actions artifact 13178973173](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525452563/artifacts/13178973173). Retained for 14 days, until 2026-11-16.
- Modules: async TCP **93%**, async UDP **93%**, bounded pipeline **100%**, deadline policy **100%** measured in the candidate audit.
- This is an unpublished source candidate. No tag, GitHub Release or PyPI upload was executed.

## Closure tracking

- Initially 6 Epics and 36 native sub-issues in GitHub M2.
- 35/36 sub-issues and 5/6 Epics are closed at the time this report is prepared; final issue `PNK-M2-036` and E05 Epic will be closed after the technical closure PR merges and main CI passes.
- Native GitHub Project #9 view and Status field reconciliation could not be independently audited with the available connector access. Issue states and parent/child completion are independently recorded in GitHub; do not claim all Project cards are `Done` without running `scripts/github/m2_project_bootstrap.sh --verify` with Project-scoped auth.
- The closing report and exact final-main CI run will be linked to the final Epic issue.
