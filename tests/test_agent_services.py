import asyncio
import pytest
from aioconsul import Consul
from util import async_test

@async_test
def test_services():
    client = Consul()
    services = yield from client.agent.services.items()
    assert len(services)
    assert services[0].id == 'consul'

    service1 = yield from client.agent.services.get('consul')
    assert services[0] == service1

    with pytest.raises(client.agent.services.NotFound):
        srv = yield from client.agent.services.get('foo')
    srv = yield from client.agent.services.register('foo',
                                                    address='127.0.0.1',
                                                    port=6666)
    assert srv.id == 'foo'
    assert srv.address == '127.0.0.1'
    assert srv.port == 6666


@async_test
def test_service_with_http_check():
    client = Consul()
    name = 'bar'
    with pytest.raises(client.agent.services.NotFound):
        srv = yield from client.agent.services.get(name)
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get('service:%s' % name)

    srv = yield from client.agent.services.register_http(name,
                                                         'http://example.com',
                                                         interval='1s')
    assert srv.name == name
    yield from asyncio.sleep(2)

    srv = yield from client.agent.services.get(name)
    check = yield from client.agent.checks.get('service:%s' % name)
    assert srv.id == name
    assert check.id == 'service:%s' % name
    assert check.status == 'passing'


@async_test
def test_service_with_http_check_fail():
    client = Consul()
    name = 'baz'
    with pytest.raises(client.agent.services.NotFound):
        srv = yield from client.agent.services.get(name)
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get('service:%s' % name)

    srv = yield from client.agent.services.register_http(name,
                                                         'http://dummy.example.com',
                                                         interval='1s')
    assert srv.name == name
    yield from asyncio.sleep(2)

    srv = yield from client.agent.services.get(name)
    check = yield from client.agent.checks.get('service:%s' % name)
    assert srv.id == name
    assert check.id == 'service:%s' % name
    assert check.status == 'critical'


@async_test
def test_service_with_script_check():
    client = Consul()
    name = 'bar'
    with pytest.raises(client.agent.services.NotFound):
        srv = yield from client.agent.services.get(name)
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get('service:%s' % name)

    srv = yield from client.agent.services.register_script(name,
                                                           'true',
                                                           interval='1s')
    assert srv.name == name
    yield from asyncio.sleep(2)

    srv = yield from client.agent.services.get(name)
    check = yield from client.agent.checks.get('service:%s' % name)
    assert srv.id == name
    assert check.id == 'service:%s' % name
    assert check.status == 'passing'


@async_test
def test_service_with_script_check_fail():
    client = Consul()
    name = 'bar'
    with pytest.raises(client.agent.services.NotFound):
        srv = yield from client.agent.services.get(name)
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get('service:%s' % name)

    srv = yield from client.agent.services.register_script(name,
                                                           'false',
                                                           interval='1s')
    assert srv.name == name
    yield from asyncio.sleep(2)

    srv = yield from client.agent.services.get(name)
    check = yield from client.agent.checks.get('service:%s' % name)
    assert srv.id == name
    assert check.id == 'service:%s' % name
    assert check.status == 'warning'


@async_test
def test_service_with_ttl_check():
    client = Consul()
    name = 'foo'
    with pytest.raises(client.agent.services.NotFound):
        srv = yield from client.agent.services.get(name)
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get('service:%s' % name)

    srv = yield from client.agent.services.register_ttl(name, '10s')
    assert srv.name == name

    srv = yield from client.agent.services.get(name)
    check = yield from client.agent.checks.get('service:%s' % name)
    assert srv.id == name
    assert check.id == 'service:%s' % name