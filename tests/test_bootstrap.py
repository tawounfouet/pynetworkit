"""M0 E0 smoke tests: packaging and importable namespace."""

from importlib import metadata

import pynetworkkit


def test_version_matches_distribution_metadata() -> None:
    assert pynetworkkit.__version__ == metadata.version("pynetworkkit")


def test_layer_namespaces_import_without_network_side_effects() -> None:
    import pynetworkkit.adapters  # noqa: F401
    import pynetworkkit.domain  # noqa: F401
    import pynetworkkit.ports  # noqa: F401
