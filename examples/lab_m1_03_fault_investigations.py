"""M1 lab 03: deterministic errors, timeouts and closed resource checks."""
from __future__ import annotations

from pynetworkkit.adapters.socket import SocketTCPConnector, SocketTCPListener, SocketUDPChannel
from pynetworkkit.domain import IPEndpoint
from pynetworkkit.ports import StreamClosedError


def main() -> None:
    localhost = IPEndpoint.parse("127.0.0.1", 0)
    with SocketTCPListener.bind(localhost) as listener:
        try:
            listener.accept(timeout=0.02)
        except TimeoutError:
            pass
        else:
            raise AssertionError("accept must time out without a client")

        with SocketTCPConnector().connect(listener.local_endpoint, timeout=2) as client:
            accepted, _ = listener.accept(timeout=2)
            accepted.close()
            assert client.read(1, timeout=2) == b""

    channel = SocketUDPChannel.bind(localhost)
    channel.close()
    channel.close()
    try:
        channel.recv_from(1, timeout=0.02)
    except StreamClosedError:
        pass
    else:
        raise AssertionError("closed channel must reject recv_from")
    print("lab_m1_03: timeout, TCP EOF and closed UDP channel OK")


if __name__ == "__main__":
    main()
