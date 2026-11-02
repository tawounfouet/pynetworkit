# ADR-M1-01 - Synchronous capability ports and partial TCP I/O

- Status: PROPOSED - maintainer acceptance required before E01/E02 implementations
- Date: 2026-11-02
- Issues: #37, #38; prerequisite audit #36
- Scope: M1/E00, no OS socket adapters

## Context and decision

M0 exposes AsyncByteStream.write(bytes) -> None and aclose(), backed by
an in-memory async transport. M1 must not silently reuse this shape for
blocking OS socket calls: socket.send() can accept only a prefix.

Introduce four separate protocols via pynetworkkit.ports:
SyncByteStream, SyncStreamConnector, SyncStreamListener, SyncDatagramChannel.
Reuse IPEndpoint and Port; preserve M0 async exports and semantics.

SyncByteStream.read(max_bytes: int) -> bytes:
- Requires an integer > 0 (reject bool), yields 1..max_bytes bytes on data;
  b"" exclusively represents peer EOF. It is not a complete application
  message. A reset/timeout raises and is never encoded as b"".
- write(data: bytes) -> int: a single send-like operation. Empty data returns
  zero. For nonempty data, success must report 1..len(data) accepted bytes.
  A kernel return of zero for nonempty data becomes a transport failure,
  not a busy retry loop. Callers must handle partial writes.
- write_all() is deliberately NOT a port method in E00. A future helper,
  if justified, must use an overall monotonic deadline and fail on zero
  progress, preserving a documented accepted-prefix caveat.
- shutdown_write() is a TCP half-close; it leaves the read direction usable.
  close() is an idempotent full local close, and subsequent I/O raises
  StreamClosedError. Repeated shutdown_write after shutdown is idempotent;
  shutdown_write after close fails deterministically.
- Streams, listeners and UDP channels are context managers whose __exit__
  closes without suppressing the original exception. Connectors are
  stateless factories, not owners of returned handles.

SyncStreamConnector.connect(remote: IPEndpoint, *, timeout: float | None = None)
-> SyncByteStream. Port(0) is valid for local bind, NOT for remote connect.

SyncStreamListener.accept(*, timeout: float | None = None)
-> tuple[SyncByteStream, IPEndpoint]; local_endpoint is observable.
The accepted stream owns the accepted socket, not the listener.

## Compatibility boundary

Never introduce sync methods on AsyncByteStream or change its return type;
never derive a sync Protocol from an async Protocol. These are independent
interfaces connected through reusable domain values, not interchangeable
execution models. Structural typing enforces capability composition (DIP/ISP).

## Verification and sign-off

The E00 PR supplies shape/import/type tests and pre-adapter behavior
examples. Real network, EOF, shutdown, zero send and timeout behavior
must be qualified again against E01 socket adapters. CI green is NOT
an acceptance of this proposed ADR.

Alternatives rejected: sendall() as write() (hides partial I/O), a single
universal TCP/UDP interface, implicit socket lifecycle in the domain.
