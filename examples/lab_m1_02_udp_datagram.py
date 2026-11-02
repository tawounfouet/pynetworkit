"""M1 lab 02: datagrams and explicit truncation over IPv4 loopback."""
from __future__ import annotations

from pynetworkkit.adapters.socket import SocketUDPChannel
from pynetworkkit.domain import IPEndpoint


def main() -> None:
    local = IPEndpoint.parse("127.0.0.1", 0)
    with SocketUDPChannel.bind(local) as sender, SocketUDPChannel.bind(local) as recipient:
        recipient_address = recipient.local_endpoint
        sender.send_to(b"alpha", recipient_address, timeout=2)
        first = recipient.recv_from(5, timeout=2)
        assert first.payload == b"alpha" and not first.truncated
        assert first.source == sender.local_endpoint

        sender.send_to(b"", recipient_address, timeout=2)
        empty = recipient.recv_from(5, timeout=2)
        assert empty.payload == b"" and not empty.truncated

        sender.send_to(b"oversized", recipient_address, timeout=2)
        truncated = recipient.recv_from(3, timeout=2)
        assert truncated.payload == b"ove" and truncated.truncated
    print("lab_m1_02: UDP source, empty payload and truncation OK")


if __name__ == "__main__":
    main()
