"""M1 lab 01: bounded TCP echo over local IPv4 loopback."""
from __future__ import annotations

import threading

from pynetworkkit.adapters.socket import SocketTCPConnector, SocketTCPListener
from pynetworkkit.domain import IPEndpoint


def main() -> None:
    errors: list[Exception] = []
    with SocketTCPListener.bind(IPEndpoint.parse("127.0.0.1", 0)) as listener:
        address = listener.local_endpoint

        def serve() -> None:
            try:
                accepted, _ = listener.accept(timeout=3)
                with accepted:
                    while chunk := accepted.read(4096, timeout=3):
                        sent = 0
                        while sent < len(chunk):
                            sent += accepted.write(chunk[sent:], timeout=3)
            except Exception as exc:
                errors.append(exc)

        worker = threading.Thread(target=serve)
        worker.start()
        try:
            with SocketTCPConnector().connect(address, timeout=3) as client:
                payload = b"hello from M1"
                written = 0
                while written < len(payload):
                    written += client.write(payload[written:], timeout=3)
                client.shutdown_write()
                incoming = bytearray()
                while len(incoming) < len(payload):
                    next_bytes = client.read(4096, timeout=3)
                    if not next_bytes:
                        raise RuntimeError("premature TCP EOF")
                    incoming.extend(next_bytes)
                assert bytes(incoming) == payload
        finally:
            worker.join(timeout=7)
            if worker.is_alive():
                raise RuntimeError("TCP lab thread failed to terminate")
        if errors:
            raise RuntimeError("TCP lab server failure") from errors[0]
    print("lab_m1_01: TCP echo, partial I/O, EOF and teardown OK")


if __name__ == "__main__":
    main()
