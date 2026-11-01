# M0 architecture decision review ledger

Status: **REVIEW REQUIRED**. This register distinguishes technical execution
evidence from an explicit architecture acceptance by the maintainer.

| ADR | Topic | Evidence available | Decision | Approval |
| --- | --- | --- | --- | --- |
| [0001](0001-python-packaging-and-naming.md) | Package baseline and naming | Repository renamed to `pynetworkkit`; E0 CI | Naming implemented; remaining decisions PROPOSED | Pending |
| [0002](0002-domain-addressing-and-lifecycle.md) | IP/CIDR types, Port, connection FSM | E1 tests and E3 property tests | PROPOSED; terminal FAILED vs CLOSED semantics need sign-off | Pending |
| [0003](0003-memory-stream-semantics.md) | Backpressure, cancellation, close | E2 contract and E3 resilience tests | PROPOSED; half-close deferred | Pending |
| [0004](0004-e3-quality-gates.md) | Coverage/security quality policy | E3 CI 9/9, observed 97%, floor 95% | Floor implemented; ADR remains PROPOSED | Pending |

## API review checklist

- [x] Enumerate the implemented M0 imports and runtime contracts.
- [x] Explain `IPAddress` / `IPNetwork` as standard-library aliases.
- [x] Make endpoint IPv6, scoped addressing and Port 0 rules explicit.
- [x] Record `CREATED` vs `NEW` and terminal `FAILED` choice from
  documents 17/19 without pretending the source specifications are identical.
- [x] Document timeout/cancellation, partial writes, full close and EOF.
- [x] Distinguish memory adapter behavior from a real TCP stack.
- [ ] Maintainer formally accepts/rejects ADR-0001 through ADR-0004.
- [ ] Approve the pre-alpha public contract for the `0.1.0a1` tag.
- [ ] Confirm API review evidence on merged `main` (not only stacked branches).

## Software Design & Learning

- DDD: Value Objects, explicit invariants and ubiquitous language.
- DIP and ISP: capability protocols separate implementations from clients.
- Ports & Adapters: memory transport substitutes in contract tests.
- KISS/YAGNI: no duplicate `ipaddress` wrappers or premature DNS/TLS stack.
- Resource ownership: make close and cancellation obligations observable.

This register does not itself accept any ADR or authorize a release.
