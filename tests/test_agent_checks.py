import asyncio
import pytest
from aioconsul import Consul
from conftest import async_test


@async_test
def test_check_ttl():
    client = Consul()
    name = 'bar'
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get(name)

    check = yield from client.agent.checks.register_ttl(name, '1s')
    assert check.name == name

    check = yield from client.agent.checks.get(name)
    assert check.name == name
    assert check.status == 'critical'

    checks = yield from client.agent.checks()
    assert check in checks

    yield from client.agent.checks.passing(check, note="that's OK")
    check = yield from client.agent.checks.get(name)
    assert check.name == name
    assert check.status == 'passing'
    assert check.output == "that's OK"

    yield from client.agent.checks.failing(check, note="oh my god!")
    check = yield from client.agent.checks.get(name)
    assert check.name == name
    assert check.status == 'critical'
    assert check.output == "oh my god!"

    yield from client.agent.checks.warning(check, note="it's becoming less than worse")
    check = yield from client.agent.checks.get(name)
    assert check.name == name
    assert check.status == 'warning'
    assert check.output == "it's becoming less than worse"

    yield from asyncio.sleep(1)

    check = yield from client.agent.checks.get(name)
    assert check.name == name
    assert check.status == 'critical'
    assert check.output == 'TTL expired'


@async_test
def test_http_check():
    client = Consul()
    name = 'bar'
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get(name)

    check = yield from client.agent.checks.register_http(name,
                                                         'http://example.com',
                                                         interval='1s')
    assert check.name == name
    yield from asyncio.sleep(2)

    check = yield from client.agent.checks.get(name)
    assert check.id == name
    assert check.status == 'passing'


@async_test
def test_http_check_fail():
    client = Consul()
    name = 'bar'
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get(name)

    check = yield from client.agent.checks.register_http(name,
                                                         'http://dummy.example.com',
                                                         interval='1s')
    assert check.name == name
    yield from asyncio.sleep(2)

    check = yield from client.agent.checks.get(name)
    assert check.id == name
    assert check.status == 'critical'


@async_test
def test_script_check():
    client = Consul()
    name = 'bar'
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get(name)

    check = yield from client.agent.checks.register_script(name,
                                                           'true',
                                                           interval='1s')
    assert check.name == name
    yield from asyncio.sleep(2)

    check = yield from client.agent.checks.get(name)
    assert check.id == name
    assert check.status == 'passing'


@async_test
def test_script_check_fail():
    client = Consul()
    name = 'bar'
    with pytest.raises(client.agent.checks.NotFound):
        check = yield from client.agent.checks.get(name)

    check = yield from client.agent.checks.register_script(name,
                                                           'false',
                                                           interval='1s')
    assert check.name == name
    yield from asyncio.sleep(2)

    check = yield from client.agent.checks.get(name)
    assert check.id == name
    assert check.status == 'warning'
