# PyNetworkKit M2 Async Core - Public API (alpha development)

## Baseline and compatibility

M2 adds native asyncio adapters but does not alter the M0 `AsyncByteStream`
and `AsyncStreamConnector` method names/signatures or the separate M1 sync
interfaces. A byte stream is not a message transport and a successful send
does not establish remote delivery.

## Ports

- `AsyncByteStream.read(max_bytes: int) -> bytes`: requires positive non-bool int; may return a partial buffer; `b""` indicates remote TCP EOF.
- `AsyncByteStream.write(data: bytes) -> None`: transfers into the transport subject to drainage, potentially partially accepted on cancellation; never retries automatically.
- `AsyncByteStream.aclose() -> None`: releases the stream, idempotent.
- `AsyncStreamConnector.connect(endpoint: IPEndpoint)`: numeric IPv4/IPv6 destination, port 1..65535.
- `AsyncStreamListener.accept() -> (AsyncByteStream, IPEndpoint)`: transfers ownership of accepted stream. Closing the listener cancels its pending accept tasks, not already accepted streams.
- `AsyncDatagramChannel.send_to(payload, destination) -> int`: complete datagram length or exception; no reliability guarantee.
- `AsyncDatagramChannel.recv_from(max_bytes) -> ReceivedDatagram`: consumes one complete datagram into a bounded 65535-byte receive and reports `truncated` if the application-requested prefix is shorter.
- `AsyncDatagramChannel.aclose() -> None`: closes its owned socket and cancels pending receivers.

## Reference implementations

```python
from pynetworkkit.adapters.asyncio import (
    AsyncioTCPConnector,
    AsyncioTCPListener,
    AsyncioUDPChannel,
)
from pynetworkkit.domain import IPEndpoint

listener = AsyncioTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0))
udp = AsyncioUDPChannel.bind(IPEndpoint.parse("127.0.0.1", 0))
```

## Application policies

- `Deadline.after(seconds)` creates an absolute monotonic deadline.
- `within_deadline(awaitable, deadline)` uses `asyncio.timeout_at`, propagating timeout without hidden retries.
- `BoundedByteQueue(max_bytes, max_items)` bounds both bytes and items. Closing wakes blocked put/get calls.
- `bounded_map(items, handler, max_tasks=n)` owns at most `n` structured worker tasks, with ordered results and TaskGroup error propagation.

## Limits and non-goals

Transport support: CPython 3.11+, tested in CI on Python 3.11-3.13,
Linux, macOS and Windows. All labs use loopback and ephemeral ports.
DNS resolution, framing, TLS and publication are outside this milestone.
Use external `asyncio.timeout` or `within_deadline` to bound operations.
Policies deliberately do not expose a new event loop or thread-based facade.

## Deliberately deferred behavior

M2 does not add a public TCP half-close method. Closing a stream is a full
local close, preserving the M0 `aclose` contract. Client application framing,
TLS and protocol helpers belong to later milestones. A cancelled write may
have queued a prefix and is never safely replayable without an application
protocol. The version `0.2.0a1` is a development candidate, not a release.
