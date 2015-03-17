import asyncio
import logging
from aioconsul import Consul
from functools import wraps

logger = logging.getLogger(__name__)


def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


@async_test
def setup_function(function):
    client = Consul()
    return


@async_test
def test_catalog_nodes():
    client = Consul()
    nodes = yield from client.catalog.nodes()
    assert set(nodes[0].keys()) == {'Address', 'Node'}
    assert nodes[0]['Node'] == 'my-local-node'


@async_test
def test_catalog_services():
    client = Consul()
    services = yield from client.catalog.services()
    assert services == {'consul': []}


@async_test
def test_catalog_datacenters():
    client = Consul()
    datacenters = yield from client.catalog.datacenters()
    assert datacenters == ['dc1']
