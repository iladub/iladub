import pytest

from iladub.substrate.fluree import FlureeEndpoint
from tests.substrate.server import check_version, find_binary, ledger_namer, running_server


@pytest.fixture(scope="session")
def fluree_endpoint():
    """(FlureeEndpoint, fresh_ledger) against a local `fluree server run --memory`."""
    binary = find_binary()
    check_version(binary)
    with running_server(binary) as (_proc, url):
        yield FlureeEndpoint(url), ledger_namer()
