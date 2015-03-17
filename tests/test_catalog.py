import asyncio
import logging
from aioconsul import Consul
from functools import wraps
from util import async_test

logger = logging.getLogger(__name__)


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
