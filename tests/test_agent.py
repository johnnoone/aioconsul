import asyncio
import logging
import pytest
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
    # remove checks
    checks = yield from client.agent.checks.items()
    for check in checks:
        yield from client.agent.checks.delete(check)

    # remove services
    services = yield from client.agent.services.items()
    for service in services:
        if service.id != 'consul':
            yield from client.agent.services.delete(service)


@async_test
def test_members():
    client = Consul()
    members = yield from client.agent.members()
    me = yield from client.agent.me()
    assert len(members) == 1
    assert me['Member'] == members[0]


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
    assert srv.name == 'foo'
    assert srv.address == '127.0.0.1'
    assert srv.port == 6666


@async_test
def test_check_ttl():
    client = Consul()
    name = 'bar'
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get(name)

    check = yield from client.agent.checks.register_ttl(name, '2s')
    assert check.name == name

    check = yield from client.agent.checks.get(name)
    assert check.name == name
    assert check.status == 'critical'

    yield from client.agent.checks.passing(check, note="that's OK")
    check = yield from client.agent.checks.get(name)
    assert check.name == name
    assert check.status == 'passing'
    assert check.output == "that's OK"

    yield from client.agent.checks.warning(check, note="it's becoming worse")
    check = yield from client.agent.checks.get(name)
    assert check.name == name
    assert check.status == 'warning'
    assert check.output == "it's becoming worse"

    yield from asyncio.sleep(4)

    check = yield from client.agent.checks.get(name)
    assert check.name == name
    assert check.status == 'critical'
    assert check.output == 'TTL expired'
