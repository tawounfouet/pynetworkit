# 31 - PyNetworkKit M3: Protocol Utilities - Handoff from M2

**Date:** 2026-11-02
**Predecessor:** M2 Async Core `0.2.0a1`
**Next planned milestone:** M3 Protocol Utilities `0.3.0a1`
**Status:** Handoff proposal, not M3 implementation or release approval.

## 1. Source of truth

The verified M2 ports remain unchanged:
`AsyncByteStream.read/write/aclose`, `AsyncStreamConnector.connect(IPEndpoint)`,
`AsyncStreamListener.accept`, and `AsyncDatagramChannel.send_to/recv_from/aclose`.

M0 in-memory stream and M2 asyncio TCP adapters pass shared contracts;
UDP preserves `ReceivedDatagram(payload, source, truncated)`.
M2 provides monotonic deadlines, TaskGroup caps and bounded byte queues.

## 2. M3 bounded scope

- Framing: length-prefixed and delimiter-based byte-stream messages,
  strict maximum frame size and incremental parsing.
- Codecs: small stateless encode/decode contracts with typed malformed
  data failures, short reads and incomplete frame handling.
- DNS resolution: a name-resolver port and standard-library-backed
  adapter, separation of hostnames from numeric `IPEndpoint`, IPv4/IPv6
  answers and explicit cache/TTL policy if justified.
- Executable offline labs that use local fake transports and bounded
  localhost tests; no unrestricted internet scans.
- Tests for malformed/oversize frames, stream segmentation, cancellation
  mid-read, parser resource budgets, and resolution failure semantics.

## 3. Architectural guardrails

- Do not reinterpret `read(n)` as returning exactly `n` bytes.
- Do not put application framing into transport adapters.
- Never treat DNS names as validated IP addresses without resolution.
- No implicit retries after partial writes or timeout.
- Keep user-supplied frame/message lengths bounded in bytes.
- Preserve M0/M1/M2 public imports and Python >=3.11.
- Reuse existing error/lifecycle contracts and make material differences
  explicit in M3 ADRs.
- Keep publication separate from milestone closure.

## 4. Candidate starting tasks

1. Inventory framing/use-case requirements, decisions and ADRs.
2. Specify `FrameCodec` and `AsyncMessageChannel` **only if** a use case
   proves a benefit beyond a simple codec function.
3. Build one length-prefix codec with a strict bytes cap and unit tests.
4. Add delimiter framing and tests for delimiters split across TCP reads.
5. Specify `AsyncNameResolver`, hostname value object and failure taxonomy.
6. Implement an async standard-library resolver adapter without blocking
   the event loop.
7. Add contract tests with memory doubles, local tests and deterministic faults.
8. Perform independent CI/security/release gate and update the roadmap.

**M3 GO criteria** require explicit new issue breakdown, ADR approval and
validation; no M3 code or PRs have been created by this handoff.
