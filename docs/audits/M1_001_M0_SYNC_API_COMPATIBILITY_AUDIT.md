# PNK-M1-001 - M0 baseline and synchronous API compatibility audit

- Date: 2026-11-02
- Issue: https://github.com/tawounfouet/pynetworkkit/issues/36
- Parent: https://github.com/tawounfouet/pynetworkkit/issues/31
- Audited main SHA: fedfc23a2a6f151bff1d83553dab7f8a94a0dcf6
- Evidence CI: https://github.com/tawounfouet/pynetworkkit/actions/runs/41330528432
- Run outcome: 9/9 successful (Linux/macOS/Windows x Python 3.11/3.12/3.13)
- Linux 3.11 job: https://github.com/tawounfouet/pynetworkkit/actions/runs/41330528432/job/124919468039
- Job logs: 121 tests passed, 97.38% combined branch/statement coverage;
  minimum CI threshold 95%; Ruff, mypy strict, isolated wheel check passed.
- Review method: source and exact-SHA GitHub Actions logs. No local
  clean-room run of the M0 repository is claimed.

## M0 public API compatibility inventory

- Root: pynetworkkit.__version__ == 0.1.0a1, not a published release.
- Domain: IPAddress/IPNetwork stdlib aliases; parse_ip_address,
  parse_ip_network; immutable Port (0..65535 excluding bool) and
  IPEndpoint; ConnectionState with CREATED/CONNECTING/ESTABLISHED/
  CLOSING/CLOSED/FAILED and pure transitions. Exceptions:
  NetworkDomainError, NetworkValidationError, InvalidConnectionTransition.
- Ports: AsyncByteStream.read(max_bytes)->bytes, write(bytes)->None,
  aclose()->None; AsyncStreamConnector.connect(IPEndpoint).
  StreamClosedError is already a public import.
- Adapter: MemoryByteStream and create_memory_stream_pair; deterministic
  bounded duplex buffers. A cancelled write may have accepted a prefix.
  Peer close yields EOF only after draining bytes. No half-close exposed.
- Architecture tests prohibit OS networking imports in domain/ports.
- Python baseline >=3.11 and zero third-party runtime dependencies.

## Findings and required safeguards

1. Async and sync write results differ: a sync port must use a partial
   count (int); never change M0 AsyncByteStream.write()->None.
2. TCP b"" on read denotes EOF; UDP b"" denotes a valid datagram.
3. UDP truncation is not observable from a plain payload/source tuple.
   Propose ReceivedDatagram(payload, source, truncated).
4. Port(0) is valid for local ephemeral bind, not remote TCP connect.
5. A socket is exclusively owned and closed on all failed connect/accept
   and bind paths. Context manager close is idempotent.
6. socket.timeout is not EOF. Keep precise causes on any OS translation.
7. Tests of memory adapters DO NOT establish correctness of real TCP
   or UDP adapters; bounded network loopback is required in E01/E02.
8. The current main branch reports protected=false and no rulesets;
   release governance must address this before publication.
9. ADR-0001..0004 remain PROPOSED pending maintainer sign-off.
10. There are 3 unexecuted statements and 3 branches in the M0
    memory stream (defensive closure paths); overall 97.38%.
11. Separate release-governance issue #29 is OPEN; no tag or PyPI
    publication is authorized merely by M1 work.

## Decision

GO: begin E00 contract-first design and typed tests on a feature branch.
CONDITIONAL: the new ADR-M1-01..06 proposals need review/acceptance
before E01/E02 concrete network adapters.
NO-GO: declare M1/E00 complete or publish 0.1.0a1 from this audit.
No change to the M0 API is necessary or authorized by this report.

## Acceptance traceability

- #36: SHA, imports, invariants, CI, compatibility gaps -> documented here.
- #37: proposed synchronous Protocol surface -> sync_streams and sync_datagrams.
- #38: TCP EOF/partial IO -> ADR-M1-01 and fake contract tests.
- #39: UDP empty/truncation -> ADR-M1-02 and typed result tests.
- #40: socket ownership/error/timeout -> ADR-M1-03/04 and matrices.

This report is a snapshot at the audited SHA; see future PR CI for
verification of M1 changes themselves. It does not change M0
release governance or claim E00 production readiness.
