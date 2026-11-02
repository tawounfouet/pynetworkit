# M2 compatibility baseline (E00)

- Baseline main commit: `c30dfbfe85e0d91338d140091b588ded82d0908a`.
- M0 unchanged: `AsyncByteStream.read(max_bytes)`, `write(data)`, `aclose()`; `AsyncStreamConnector.connect(endpoint)`.
- M1 unchanged: `SyncByteStream`, `SyncStreamConnector`, `SyncStreamListener`, `SyncDatagramChannel`, and `ReceivedDatagram(payload, source, truncated)`.
- M2 adds `AsyncStreamListener` and `AsyncDatagramChannel` without an asyncio dependency in ports/domain.
- Empty UDP datagram differs from TCP EOF; UDP truncation is observable.
- Pure ports must never import `socket` or `asyncio`.
- No source version bump or publication in the E00 PR. Version 0.2.0a1 requires a separate technical gate.
- Proof still required: nine CI jobs on the PR SHA, reviewed ADRs, merged SHA, post-merge runs.

The baseline identifies observed source signatures, not an attestation of M2 completion.
