import pytest
from aioconsul import Consul
from conftest import async_test


@async_test
def test_catalog_nodes():
    client = Consul()
    nodes = yield from client.catalog.nodes()
    assert nodes[0].name == 'my-local-node'

    with pytest.raises(client.catalog.NotFound):
        yield from client.catalog.get('foo')
    node = yield from client.catalog.get('my-local-node')
    assert node.name == 'my-local-node'
    assert node.services['consul'].name == 'consul'


@async_test
def test_catalog_services():
    client = Consul()
    services = yield from client.catalog.services()
    assert services == {'consul': []}

    nodes = yield from client.catalog.nodes(service='foo')
    assert len(nodes) == 0

    nodes = yield from client.catalog.nodes(service='consul')
    assert len(nodes) == 1

    nodes = yield from client.catalog.nodes(service='consul', tag='dumb')
    assert len(nodes) == 0


@async_test
def test_catalog_datacenters():
    client = Consul()
    datacenters = yield from client.catalog.datacenters()
    assert datacenters == ['dc1']


@async_test
def test_catalog_register_service():
    client = Consul()
    node = yield from client.catalog.get('my-local-node')
    node = {'name': 'my-local-node',
            'address': node.address}
    service = {'name': 'foo'}

    resp = yield from client.catalog.register_service(node, service=service)
    assert resp

    node = yield from client.catalog.get('my-local-node')
    assert 'foo' in node.services

    resp = yield from client.catalog.deregister_service(node, service=service)
    assert resp

    node = yield from client.catalog.get('my-local-node')
    assert 'foo' not in node.services


@async_test
def test_catalog_register_check():
    client = Consul()
    node = yield from client.catalog.get('my-local-node')
    node = {'name': 'my-local-node',
            'address': node.address}
    check = {'name': 'baz',
             'state': 'passing',
             'service_id': 'bar'}
    service = {'name': 'bar'}

    resp = yield from client.catalog.register(node, check=check, service=service)
    assert resp

    resp = yield from client.catalog.deregister(node, check=check, service=service)
    assert resp
