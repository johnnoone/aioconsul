import asyncio
import pytest
from aioconsul import Consul
from util import async_test


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

    yield from asyncio.sleep(1)

    check = yield from client.agent.checks.get(name)
    assert check.name == name
    assert check.status == 'critical'
    assert check.output == 'TTL expired'
