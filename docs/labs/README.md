# M0 Learning Labs - Software Design & Learning

All exercises run locally against a package installed from the working branch.
They do not need Internet access or privileged network permissions.

| Lab | Runnable file | Network concept | Python mechanism | Design principle |
| --- | --- | --- | --- | --- |
| 01 - IP and Port | `examples/lab01_ip_port.py` | IPv4/IPv6, CIDR, endpoint | `ipaddress`, immutable dataclass | Domain Value Object, DRY |
| 02 - Lifecycle | `examples/lab02_connection_fsm.py` | Legal state transition | `StrEnum`, pure functions | DDD invariant, KISS |
| 03 - Memory duplex | `examples/lab03_memory_duplex.py` | Byte stream, EOF, closure | `asyncio`, `Protocol`, locks | Ports & Adapters, DIP |

## Lab 01 - IP, CIDR and ports

Run: `python examples/lab01_ip_port.py`.

1. Explain why `192.0.2.10` belongs to `192.0.2.0/24`.
2. Change the prefix to `/32` and check membership for another host.
3. Inspect how an IPv6 endpoint is rendered with brackets.
4. Try `Port(True)`, `Port(-1)` and `Port(65536)`. Record the exceptions.
5. Compare a strict CIDR parse to `strict=False`: why reject or normalize host bits?

**Evidence:** output and the related unit/property tests for addressing.

## Lab 02 - Connection lifecycle

Run: `python examples/lab02_connection_fsm.py`.

1. Write out the `CREATED -> CONNECTING -> ESTABLISHED -> CLOSING -> CLOSED`
   sequence.
2. Try to reopen a CLOSED connection and explain the typed exception.
3. Compare the logical FSM to a kernel TCP state diagram. They are **not the
   same machine**.
4. Identify why terminal states and explicit transitions strengthen invariants.

**Evidence:** full 36-pair FSM matrix in `tests/unit/test_connection.py`.

## Lab 03 - Async byte streams in memory

Run: `python examples/lab03_memory_duplex.py`.

1. Show that reading two bytes followed by three bytes reconstructs `hello`.
2. Shrink `max_buffer_bytes` and use two tasks to observe backpressure.
3. Explain the difference between a byte stream and a datagram.
4. Why does cancelling a blocked write permit an accepted prefix?
5. What does `b""` mean after the sender has closed and the buffer is empty?

**Evidence:** reusable contract and resilience tests in `tests/contracts/`.

## Learning convention for each lab

State the concept, Python mechanism, design principle or pattern, alternatives
and trade-offs, and an executable observation. Keep exercises offline. For
networking with real sockets, refer to the future M1 and M2 milestones.

## Verify all labs

```bash
python -m pytest -q tests/docs/test_learning_labs.py
```

This tests the shipped programs as separate processes using the active
interpreter. It does not claim a clean wheel installation; that has its own
release gate.
