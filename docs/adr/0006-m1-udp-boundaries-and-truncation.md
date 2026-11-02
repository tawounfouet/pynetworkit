# ADR-M1-02 - UDP receive result and observable truncation

- Status: ACCEPTED for the M1 technical baseline (2026-11-02; delegated owner review)
- Date: 2026-11-02
- Issues: #37, #39

## Decision

A UDP channel transfers whole datagrams; it is not a byte stream.
SyncDatagramChannel.send_to(payload: bytes, destination: IPEndpoint) -> int
attempts ONE datagram, including b"". It must report the complete number
of payload bytes or raise. It must not implement TCP-style prefix retries.
Payload size and MTU limits depend on IP family, OS and socket settings;
OS errors are preserved as transport failures.

recv_from(max_bytes: int, *, timeout: float | None = None)
-> ReceivedDatagram(payload: bytes, source: IPEndpoint, truncated: bool).

ReceivedDatagram is a frozen, slotted value object. b"" is a legitimate UDP
payload. The truncated flag distinguishes a valid empty datagram from a
nonempty datagram received with max_bytes=0. No EOF exists for UDP receive.

Validation:
- max_bytes must be an integer (excluding bool) in 0..65535.
- payload is at most max_bytes bytes; source is a resolved IPEndpoint.
- implementations must never silently discard truncation evidence.
- Read one full UDP packet with recvfrom(65535), a bounded allocation,
  before slicing the returned bytes to the requested max_bytes.
  truncated = (len(received) > max_bytes). The datagram is fully consumed;
  any excess from the caller's perspective is lost, with no automatic replay.
- recvmsg(MSG_TRUNC) may be useful on supported OSes but MUST NOT be
  the sole implementation because its availability varies across systems.
- Using only max_bytes + 1 as the receive buffer is NOT portable: on
  Windows Winsock, a too-small recvfrom buffer can raise WSAEMSGSIZE for
  UDP, losing the excess data and potentially the typed result.
  Reference: https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-recvfrom
- Full-datagram receive distinguishes payloads over the requested
  limit without an unbounded allocation. Test with IPv4/IPv6
  loopback and system-specific socket behavior before E02 completion.
- An oversized datagram is not a reconnectable stream tail. Never
  reinterpret empty UDP payload as TCP EOF.

## Alternatives

Tuple[bytes, IPEndpoint] is inadequate: it cannot communicate truncation.
Raise-on-truncation is a defensible alternative but erases the received
prefix and source without an additional exception payload, and requires
more complex cross-OS behavior. The typed result favors explicit
observability and simple downstream handling.

## Verification

The typed result and real UDP loopback behavior are qualified on Linux,
macOS and Windows, including empty and truncated datagrams and the Winsock
small-buffer regression. Evidence:
https://github.com/tawounfouet/pynetworkkit/actions/runs/41459531092.
Accepted limitation: the 65535-byte bounded receive is a portability choice,
not a promise that every IP family can transport a 65535-byte UDP payload.
