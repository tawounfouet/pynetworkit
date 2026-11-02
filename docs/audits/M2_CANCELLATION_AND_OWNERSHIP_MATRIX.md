# M2 Cancellation, ownership and failure matrix

Status: Accepted technical semantics, subject to exact-SHA CI and change review.
Date: 2026-11-02.

| Operation | Normal outcome | Cancellation/timeout | Ownership |
| --- | --- | --- | --- |
| TCP connect | Returns stream | Propagate CancelledError or TimeoutError; no hidden retry | Caller owns returned stream |
| TCP listener accept | Returns stream and peer | Pending accept cancelled on listener close | Accepted stream ownership passes to caller |
| TCP read | bytes or EOF (`b""`) | Cancellation propagates; no synthetic EOF | Stream owner must close |
| TCP write | bytes queued with awaited `drain` | Prefix may be accepted; no implicit retry | Stream owner closes on workflow termination |
| TCP aclose | closed stream | A cancelled close can be retried idempotently | Stream owner initiates close |
| UDP send_to | Entire datagram length | Failure is not a delivery guarantee | Channel owner closes |
| UDP recv_from | ReceivedDatagram with source and truncation | Cancellation is not EOF | Channel owner closes |
| UDP aclose | Socket closed | Pending receives cancelled and cleanup idempotent | Channel is exclusive owner |
| Queue put/get | Byte/item bounded | No credit leaks; close wakes waiters | Queue owner calls aclose |
| TaskGroup bounded_map | Input-order results | Sibling tasks are cancelled on failure | TaskGroup owns all worker tasks |

No user-space TCP/IP stack, DNS resolution, TLS or raw packet capture are part of M2.
A partial write is not safely retryable without application-level idempotency.
Tests must not depend on external internet services or wall-clock sleeps.

## Deferred

TCP half-close is not exposed by the M0 `AsyncByteStream` contract and remains
deliberately deferred. UDP datagrams are messages, not EOF-terminated streams.
The adapter uses 65535 bytes for the OS-level receive buffer and applies
the requested `max_bytes` limit afterwards, preserving portable truncation evidence.
