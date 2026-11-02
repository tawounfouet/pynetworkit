# M2 Async Core - Six executable labs

Install from a source checkout (`python -m pip install -e '.[dev]'`).
No external Internet access is used.

| Lab | Run | Mechanism |
| --- | --- | --- |
| 01 | `python examples/lab_m2_01_tcp_echo.py` | TCP echo, partial reads, ownership |
| 02 | `python examples/lab_m2_02_udp_datagram.py` | UDP sender, empty payload, truncation |
| 03 | `python examples/lab_m2_03_cancel_deadline.py` | Absolute timeout and cancellation |
| 04 | `python examples/lab_m2_04_backpressure.py` | Slow consumer and bounded byte credits |
| 05 | `python examples/lab_m2_05_concurrent_clients.py` | TaskGroup, ten clients, three worker slots |
| 06 | `python examples/lab_m2_06_failures.py` | Closed-channel typed errors |

## Learning goals

1. Contrast blocking socket operations from M1 with nonblocking native asyncio.
2. Trace ownership across bind, connect, accept, stream close and listener close.
3. Explain why TCP read boundaries differ from UDP datagram boundaries.
4. Distinguish cancellation/timeout from EOF and successful delivery.
5. Demonstrate that producer throughput is bounded by consumer capacity.
6. Measure the number of simultaneous tasks and verify cleanup on failure.

Every lab must run in CI; reproducible failing scenarios should carry the
exact Python version, OS, commit SHA and test name.
