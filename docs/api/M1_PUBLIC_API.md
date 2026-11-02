# PyNetworkKit M1 - Synchronous socket API reference

- Milestone: M1 Socket Kernel, candidate implementation.
- Target development version: `0.1.0a2`. No tag or release implied.
- Source: `src/pynetworkkit/ports/sync_streams.py`,
  `src/pynetworkkit/ports/sync_datagrams.py`,
  `src/pynetworkkit/adapters/socket/`.
- M0 async types, factories, and domain invariants are preserved.

## Public imports

```python
from pynetworkkit.domain import IPEndpoint, Port
from pynetworkkit.ports import (
    SyncByteStream,
    SyncStreamConnector,
    SyncStreamListener,
    SyncDatagramChannel,
    ReceivedDatagram,
    StreamClosedError,
)
from pynetworkkit.adapters.socket import (
    SocketTCPStream, SocketTCPConnector, SocketTCPListener, SocketUDPChannel,
)
```

## Contract matrix

| Capability | Operation | Result | Semantics |
| --- | --- | --- | --- |
| SyncByteStream | read(n, timeout=None) | bytes | 1..n data, b"" = TCP EOF |
| SyncByteStream | write(data, timeout=None) | int | 1..len(data) accepted, possible partial; empty -> 0 |
| SyncByteStream | shutdown_write() | None | TCP write-half close, reads remain |
| SyncByteStream | close() | None | Idempotent, own handle released |
| SyncStreamConnector | connect(remote, timeout=None) | SyncByteStream | Remote port 0 invalid; ownership returned |
| SyncStreamListener | accept(timeout=None) | stream, peer | New stream owns accepted socket |
| SyncStreamListener | local_endpoint | IPEndpoint | Real port after bind 0 |
| SyncDatagramChannel | send_to(bytes, destination, timeout=None) | int | Exactly one datagram or failure |
| SyncDatagramChannel | recv_from(max_bytes, timeout=None) | ReceivedDatagram | payload, source and truncated |
| SyncDatagramChannel | close() | None | Idempotent; subsequent operations fail |

`SocketTCPStream` additionally exposes `local_endpoint` and
`remote_endpoint`. All socket-backed resources support context managers.
A connector is a factory and does not own returned sockets.

## TCP rules

TCP is an ordered byte stream. A write can return a positive short count.
A caller responsible for whole payload delivery must implement a bounded
loop and a global deadline. Socket send returning 0 on a nonempty write
raises ConnectionError, never retries indefinitely.

A zero-length read is not accepted: `read(n)` requires positive int, not
bool. `b""` only means EOF after the peer's write half closes or closes.
Read/write after full local close raises `StreamClosedError`.
Repeated `close()` is safe; `shutdown_write()` only closes writes.

## UDP rules

Each `recv_from` consumes one entire datagram, even when `max_bytes`
exposes only a prefix. `truncated=True` marks that prefix; excess
bytes are not retained. Empty UDP payload `b""` is valid and is
distinguished from an oversized message clipped to zero bytes by
the `truncated` flag.

The adapter reads into a bounded 65535-byte UDP receive buffer to avoid
WSAEMSGSIZE on Winsock for a smaller-than-packet buffer, then slices
to `max_bytes` in 0..65535. It does not depend on POSIX `recvmsg`.
A datagram send must succeed in full (even empty) or raise.
No delivery/order/uniqueness guarantees are made.

## Ownership, errors, timeouts

Socket ownership is exclusive and explicit:
- `SocketTCPConnector.connect` hands a successfully connected socket to
  the stream; failed attempts close their temporary handles.
- `SocketTCPListener.accept` hands an accepted socket to its returned stream.
  Listener closure does not close previously accepted connections.
- `SocketUDPChannel.bind` retains ownership of its bound datagram socket.
- `with` and `close()` release resources. Concurrent use of a single
  socket with different temporary timeouts is unsupported.

A timeout of None means blocking (possibly indefinitely). Finite positive
timeouts should be specified for tests and fault-prone operations. Zero is
nonblocking OS behavior and may raise when data is unavailable. Negative,
infinite, NaN, bool and nonnumeric timeouts are rejected. TimeoutError
is distinct from TCP EOF and UDP empty data.

OS errors remain OSError subclasses with their errno, except for an
explicitly validated send-zero case raising ConnectionError. No catch-all
silently transforms network failures into empty bytes.

## IP policy and limitations

Use only numeric IPv4/IPv6 IPEndpoints. DNS and scoped IPv6 identifiers
are outside the M1 contract. IPv4 and IPv6 sockets use distinct families.
Tests require IPv4 loopback and gate IPv6 loopback by environment support.
No TLS, HTTP, resolver, multicast, full network simulation or external
network traffic is provided. Python >=3.11 with no runtime third-party
dependencies.

## Compatibility with M0

M0's AsyncByteStream.write(bytes) -> None and aclose() are unchanged and
remain separate from blocking SyncByteStream.write(bytes) -> int and close().
No implicit sync/async bridge or conversion is promised.
See ADR-M1-01..06 for options and decisions pending maintainer sign-off.
