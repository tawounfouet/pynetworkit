# M0 public API and behavioral contract - pre-alpha 0.1.0a1

Status: proposed API review; implementation evidence resides in stacked PRs
[#5](https://github.com/tawounfouet/pynetworkkit/pull/5),
[#11](https://github.com/tawounfouet/pynetworkkit/pull/11),
[#16](https://github.com/tawounfouet/pynetworkkit/pull/16) and
[#21](https://github.com/tawounfouet/pynetworkkit/pull/21).
This is an **implementation snapshot**, not a stability promise or
a statement that `main` already contains the package.

## Publicly importable symbols

| Import | API | Core semantics |
| --- | --- | --- |
| `pynetworkkit` | `__version__` | Dynamic packaging version source, planned `0.1.0a1` |
| `pynetworkkit.domain` | `IPAddress`, `IPNetwork` | Standard-library `ipaddress` union aliases |
| `pynetworkkit.domain` | `parse_ip_address(value: str)` | Numeric IP literal only, no DNS |
| `pynetworkkit.domain` | `parse_ip_network(value: str, *, strict=True)` | CIDR, strict host-bit policy by default |
| `pynetworkkit.domain` | `Port(value: int)` | Immutable, hashable, 0 through 65535; rejects bool |
| `pynetworkkit.domain` | `IPEndpoint(address, port)` | Immutable IP + Port; `parse(address, port)` helper; IPv6 brackets |
| `pynetworkkit.domain` | `ConnectionState` | `CREATED`, `CONNECTING`, `ESTABLISHED`, `CLOSING`, `CLOSED`, `FAILED` |
| `pynetworkkit.domain` | `can_transition`, `transition_state` | Pure finite-state transition policy |
| `pynetworkkit.domain` | `NetworkDomainError`, `NetworkValidationError`, `InvalidConnectionTransition` | Typed domain failures |
| `pynetworkkit.ports` | `AsyncByteStream` | Structural async read/write/close contract |
| `pynetworkkit.ports` | `AsyncStreamConnector` | Contract for opening a stream to a resolved endpoint |
| `pynetworkkit.ports` | `StreamClosedError` | Stream operation invalid after shutdown |
| `pynetworkkit.adapters.memory` | `MemoryByteStream`, `create_memory_stream_pair` | In-process duplex stream test double |

The `IPAddress` and `IPNetwork` aliases are not independent wrappers:
they preserve Python standard-library `ipaddress` types and behavior.

## Domain validation

- `parse_ip_address` accepts only numeric IP literals and rejects IPv6
  zone identifiers (`%eth0`) until an explicit zone model exists.
- `parse_ip_network` accepts CIDR and rejects networks with host bits by
  default; `strict=False` normalizes the network address. A wrong argument
  type raises `TypeError`, invalid text raises `NetworkValidationError`.
- `Port(0)` is a valid number representing ephemeral local bind intent.
  A future destination policy must decide when port zero is forbidden.
- `IPEndpoint` expects `ipaddress` objects and `Port` as members.
  `IPEndpoint.parse("2001:db8::1", 443)` displays `[2001:db8::1]:443`.
  There is no hostname support or implicit DNS query.
- Logical state transitions are not the complete TCP kernel state diagram.
  `CLOSED` and `FAILED` are terminal in this implementation.

## Asynchronous stream contract

```python
from pynetworkkit.adapters.memory import create_memory_stream_pair

left, right = create_memory_stream_pair(max_buffer_bytes=8)
```

- `await stream.read(max_bytes)` requires a strictly positive integer and
  returns at most that many bytes. If remote writer closes, already-accepted
  bytes are drained first, then reads return `b""` (EOF).
- `await stream.write(data)` requires `bytes`. It may block when the
  capacity is reached. Completion indicates all bytes were accepted into
  this adapter, **not** acknowledgment by the receiving application.
- Canceling an in-flight write may leave a prefix in the peer's buffer.
  Canceling a blocked read does not consume data until the read completes.
- `await stream.aclose()` is a *full local close* and idempotent. Local
  reads/writes then raise `StreamClosedError`; remote readers observe EOF
  after consuming buffered bytes. Half-close is not exposed in M0.
- `max_buffer_bytes` must be a positive integer, excluding bool.
  Both directions have independent finite buffer limits.
- Concurrent read requests and write requests on one endpoint are serialized
  by the in-memory adapter. This is a documented adapter behavior, not a
  transport-independent fairness guarantee.

## Error summary

| Failure | Exception |
| --- | --- |
| Invalid IP/CIDR literal, out-of-range Port, scoped IPv6 endpoint | `NetworkValidationError` |
| Wrong input type | `TypeError` (or `ValueError` for read length/capacity policy) |
| Illegal logical connection transition | `InvalidConnectionTransition` |
| Read or write after closing the local stream | `StreamClosedError` |
| Canceled blocked coroutine | `asyncio.CancelledError` |
| Application-enforced deadline | `TimeoutError` from `asyncio.wait_for` |

## Explicit non-goals and compatibility

There is **no** production TCP/UDP adapter, DNS resolver, TLS client,
real network probe, HTTP stack, or general network simulator in M0.
The adapter does not reproduce TCP congestion, segmentation or packet loss.

The API is pre-alpha; backward compatibility is not promised before
the 1.0.0 stability review. Observe the ADR register and document any breaking
change before extending transport contracts in M1/M2.
