# ADR-0003 - Bounded memory stream semantics

- Status: PROPOSED, pending review
- Milestone: M0 E2
- Date: 2026-11-01
- References: PyNetworkKit documents 10, 12, 15, 18 and 19
- Related issues: PNK-M0-010 through PNK-M0-013

## Context

M0 needs a small, deterministic, async stream adapter so contracts can be
verified without accessing the OS network stack or third-party hosts.

## Proposed decisions

1. Keep `AsyncByteStream` and `AsyncStreamConnector` as narrow `typing.Protocol`
   capability contracts. No `asyncio` or socket dependency in the pure domain
   or in the ports themselves.
2. `read(n)` requires a positive integer and returns up to n bytes, never
   application-message boundaries. `b""` means peer EOF only after all
   accepted bytes are consumed.
3. `write(data)` accepts only bytes. An empty payload is a no-op on an open
   stream. Nonempty writes apply byte-bounded backpressure and do not promise
   delivery or remote application processing.
4. A cancelled, blocked write may have accepted an initial prefix. No implicit
   rollback or exactly-once delivery guarantee. A cancelled read does not
   consume bytes until the read operation actually returns.
5. One read and one write at a time per endpoint, serialized by direction.
6. `aclose()` is full local close: no subsequent local reads or writes, and the
   remote peer observes EOF after draining previously accepted data. It is
   idempotent; it wakes pending operations. Remote writes fail when the
   receiving endpoint has closed. Half-close is deferred.
7. `create_memory_stream_pair(max_buffer_bytes=65536)` connects two endpoints
   using two independently bounded byte buffers. No worker tasks, timers,
   sleeps or external sockets are required.
8. The memory adapter is a testing double, not a model of real TCP segmentation,
   congestion, retransmission, TLS, DNS or remote failure semantics.
9. No memory connector is exposed yet: the pair factory is a local testing
   primitive. A connector implementation requires a concrete acceptance use case.

## Alternatives considered

- `asyncio.Queue[bytes]` with a bounded item count: rejects neither large byte
  payloads nor unbounded memory in individual queue items.
- Unbounded bytes buffer: simple but dangerous under a slow consumer.
- Event-loop-independent simulation runtime: postponed until M6.
- Exposing half-close now: postponed until M1/M2 semantics are reviewed.

## Verification

- Reusable behavioral assertions for bytes, partial reads, EOF and close.
- Memory-specific tests for bounded backpressure, cancellation, local and
  remote closure, invalid inputs and repeated shutdown.
- CI checks for Python 3.11/3.12/3.13 on Linux, macOS and Windows.
- No assertion of real TCP correctness based on memory tests alone.

## Risk and follow-up

Explicitly document partial writes on cancellation; a caller that requires
all-or-nothing application messages must implement framing/acknowledgment
at the appropriate higher-level protocol. Review these choices before
promoting ADR-0003 to ACCEPTED.
