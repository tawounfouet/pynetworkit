# PyNetworkKit M1 - Socket Kernel hands-on labs

All M1 lab traffic is restricted to `127.0.0.1`, with ephemeral ports
allocated by the operating system. No Internet access, DNS or privileged
ports are necessary. The labs use only Python standard-library sockets.

## Run

After installing `python -m pip install -e '.[dev]'`:

```bash
python examples/lab_m1_01_tcp_echo.py
python examples/lab_m1_02_udp_datagram.py
python examples/lab_m1_03_fault_investigations.py
```

Expected:

```text
lab_m1_01: TCP echo, partial I/O, EOF and teardown OK
lab_m1_02: UDP source, empty payload and truncation OK
lab_m1_03: timeout, TCP EOF and closed UDP channel OK
```

### Lab M1-01 - TCP Echo

- **Concept:** TCP transfers an ordered byte stream, not records or messages.
- **Primitive:** `socket.recv` may return fewer than requested, and
  `socket.send` may accept only part of the input.
- **Pattern:** TCP listener + connector + owned streams; explicit send loop.
- **Exercise:** Change the read chunk size to 2 and explain why the payload
  still round-trips. Compare `shutdown_write()` with `close()`.
- **Evidence:** integration test with bounded thread join and EOF assertion.

### Lab M1-02 - UDP

- **Concept:** Each UDP receive consumes one datagram. Empty `b""` is data.
- **Primitive:** `recvfrom(65535) followed by a bounded payload slice` permits observable truncation.
- **Pattern:** `ReceivedDatagram(payload, source, truncated)` Value Object.
- **Exercise:** Change receive limit to 0, 3 and 9; record the flag. Why
  does a subsequent receive not return the dropped bytes?
- **Evidence:** real UDP loopback tests, IPv4 and capability-gated IPv6.
- **Non-goals:** no promise of delivery, order or uniqueness across networks.

### Lab M1-03 - Investigating failures

- **Concept:** socket timeout, peer EOF and locally closed channel are
  different terminal events.
- **Primitive:** per-operation timeouts and context managers.
- **Pattern:** exclusive resource ownership, predictable exception classes.
- **Exercise:** remove a timeout argument and explain why a lab could hang.
  Discuss refusal, bind-in-use, double close and OSError preservation.
- **Evidence:** deterministic failure-injection suite and bounded timeouts.

## Contract boundaries and portability

M0 asynchronous memory streams remain independent of M1 synchronous OS
adapters. Network operations may block or raise, and the real stack does
not promise TCP message boundaries. IPv6 loopback may be unavailable and
is skipped on unsupported runners. No TLS, DNS, HTTP or full simulation
runtime is implemented in M1.

See `docs/adr/0005-m1-sync-ports-and-partial-io.md` and related M1 ADRs.
