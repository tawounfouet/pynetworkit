"""No implicit sync-to-async bridge in the new transport API."""

from pynetworkkit.adapters.asyncio import AsyncioTCPConnector, AsyncioTCPListener
from pynetworkkit.ports import AsyncByteStream, AsyncStreamConnector, AsyncStreamListener


def test_port_members_are_structurally_available() -> None:
    assert callable(AsyncioTCPConnector.connect)
    assert callable(AsyncioTCPListener.accept)
    assert callable(AsyncioTCPListener.aclose)
    assert hasattr(AsyncByteStream, "read")
    assert hasattr(AsyncStreamConnector, "connect")
    assert hasattr(AsyncStreamListener, "accept")
