# ADR-M1-03/04 - Exclusive socket ownership, timeouts and errors

- Status: PROPOSED - maintainer acceptance required before E01/E02
- Date: 2026-11-02
- Issues: #37, #38, #39, #40

## Ownership and lifecycle

One owner per socket handle. A successful connect transfers a new
connected handle from the connector to SyncByteStream; a failed connect
closes the temporary handle without masking the original failure.

The listener owns its listening handle. Each successful accept transfers
the accepted handle to its stream. Closing the listener does NOT close
previously accepted streams. A UDP channel owns its bound socket.
Wrapping an existing socket transfers ownership only through an explicit
adaptor factory/constructor contract, never by implicit sharing.

close() is idempotent. Context manager __exit__ closes and never
suppresses exceptions. Post-close read/write/send/receive/accept must
fail predictably. shutdown_write is TCP-only and different from the
M0 asynchronous aclose full close.

## Timeout model

A timeout argument is an operation-local bound in seconds, float | None.
None means the socket's normal blocking mode (potentially indefinite);
negative, NaN and infinite values are invalid and must be rejected
before a syscall. Zero may mean immediate nonblocking intent only when
the adapter documents its portability; until E01/E02 decide, use
positive finite timeout or None in callers.

A single-operation timeout is NOT an end-to-end transfer deadline.
A future write_all helper must compute a monotonic global deadline
and not restart the full time budget after each partial send.
No I/O or DNS resolution occurs in domain/ports modules.

## Error mapping

- M0 NetworkValidationError and the domain FSM remain unchanged.
- Locally closed stream operations raise existing StreamClosedError.
- Locally closed listener/channel operations use a distinct,
  explicitly documented close error (not UDP EOF).
- Genuine OS socket errors remain OSError (or a reviewed subclass).
  Do not erase errno. Any translation MUST chain with 'raise ... from exc'.
- socket.timeout / TimeoutError is a timeout outcome, not TCP EOF.
- send() returning 0 with nonempty bytes is a failure, not a success.
- Never swallow BaseException or suppress KeyboardInterrupt/SystemExit.
- If close during another operation is requested across threads, no
  portable instantaneous unblock guarantee is made.

## Verification criteria for E01/E02/E03

Fault injection: connect refused, bind in use, accept timeout, recv
reset, send zero, send partial, UDP oversized, double close, full close,
write-side shutdown, and already-closed handle. Use bounded loopback
tests and strict cleanup; assert OSError cause when translated.
