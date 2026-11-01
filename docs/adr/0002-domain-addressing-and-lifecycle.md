# ADR-0002: IP aliases, value objects and connection lifecycle

- Status: PROPOSED, pending maintainer review
- Milestone: M0 / E1
- Date: 2026-11-01
- References: documents 07, 08, 17, 18, 19

## Context

Document 17 proposes ConnectionState.CREATED and a terminal FAILED.
Document 19 sketches ConnectionState.NEW with FAILED -> CLOSED.
These illustrative contracts differ and need an explicit decision.

## Proposed decisions

1. Use Python standard-library ipaddress types as IPAddress and IPNetwork
   type aliases rather than constructing duplicate wrappers. Explicit
   parse_ip_address and parse_ip_network helpers validate input without DNS.
2. Reject scoped IPv6 literals until an interface-zone model is designed;
   never discard zone identifiers silently.
3. Define Port as an immutable slotted value object accepting integers 0..65535,
   excluding bool. Port 0 is valid for ephemeral local binds; application
   destination rules will be imposed later.
4. Define IPEndpoint as immutable validated IP + Port; display IPv6 endpoints
   in brackets, e.g. [::1]:443. No hostname resolution is implicit.
5. Use CREATED, CONNECTING, ESTABLISHED, CLOSING, CLOSED and FAILED states.
   Permit CREATED -> CLOSED and CONNECTING -> CLOSING for early termination.
   CLOSED and FAILED are terminal. Adapter idempotent close does not imply
   an additional domain state transition.
6. No socket, asyncio, DNS or operating system calls in the pure domain.

## Rationale and trade-offs

- Domain aliases preserve stdlib semantics while avoiding unnecessary code.
  Wrappers can be introduced later only for validated use cases.
- A terminal FAILED state is simpler, while adapters still own resource cleanup.
- Unsupported IPv6 scope is explicit rather than silently wrong.
- The lifecycle is application-facing, not a complete TCP state machine.

## Evidence and follow-up

- Unit tests validate CIDR strictness, IPv4/IPv6 families, Port boundaries,
  endpoint equality and hashing, immutability, scope rejection and all 36
  possible state pairs.
- Before accepting this ADR, review the chosen public API and CI evidence.
