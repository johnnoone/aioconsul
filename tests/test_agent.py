import asyncio
from aioconsul import Consul
from functools import wraps

import logging

logger = logging.getLogger(__name__)


# start a local agent for testing
# consul agent -data-dir=/tmp/consul -server -bootstrap-expect=1

def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


@async_test
def test_catalog_nodes():
    client = Consul()
    nodes = yield from client.catalog.nodes()
    assert nodes == [{'Address': '10.5.0.142', 'Node': 'plissken.cafe.intra'}]


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


@async_test
def test_kv_no_lock():
    client = Consul()

    try:
        value = yield from client.kv.get('foo')
    except client.kv.NotFound:
        logger.info('it was not found, it is OK')
    else:
        logger.info('was found! check now')
        assert value == 'bar'
        assert value.consul.key == 'foo'

    setted = yield from client.kv.set('foo', 'bar')
    assert setted

    value = yield from client.kv.get('foo')
    assert value == 'bar', value

    deleted = yield from client.kv.delete('foo')
    assert deleted, deleted
