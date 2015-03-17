import pytest
from aioconsul import Consul
from util import async_test


@async_test
def test_catalog_nodes():
    client = Consul()
    nodes = yield from client.catalog.nodes.items()
    assert nodes[0].name == 'my-local-node'

    with pytest.raises(client.catalog.nodes.NotFound):
        yield from client.catalog.nodes.get('foo')
    node = yield from client.catalog.nodes.get('my-local-node')
    assert node.name == 'my-local-node'
    assert node.services['consul'].name == 'consul'


@async_test
def test_catalog_services():
    client = Consul()
    services = yield from client.catalog.services.items()
    assert services == {'consul': []}

    with pytest.raises(client.catalog.services.NotFound):
        yield from client.catalog.services.get('foo')
    srv = yield from client.catalog.services.get('consul')
    assert srv.service == 'consul'
    with pytest.raises(client.catalog.services.NotFound):
        yield from client.catalog.services.get('consul', tag='dumb')


@async_test
def test_catalog_datacenters():
    client = Consul()
    datacenters = yield from client.catalog.datacenters()
    assert datacenters == ['dc1']
