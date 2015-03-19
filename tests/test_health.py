import asyncio
import pytest
from aioconsul import Consul
from util import async_test


@async_test
def test_health():
    client = Consul()

    for check in (yield from client.health.node('my-local-node')):
        print(check.__dict__)
        assert check.status == 'passing', check.__dict__

    # create a bunch of services for the continuing tests
    tasks = [
        asyncio.async(client.agent.services.register_ttl('foo', '10s')),
        asyncio.async(client.agent.services.register_ttl('bar', '10s')),
        asyncio.async(client.agent.services.register_ttl('baz', '10s')),
    ]
    done, pending = yield from asyncio.wait(tasks)

    tasks = [
        asyncio.async(client.agent.checks.mark('service:foo', 'pass')),
        asyncio.async(client.agent.checks.mark('service:bar', 'warn')),
        asyncio.async(client.agent.checks.mark('service:baz', 'fail')),
    ]
    done, pending = yield from asyncio.wait(tasks)

    for check in (yield from client.health.checks('serfHealth')):
        assert check.status == 'passing'

    for node in (yield from client.health.service('foo', state='any')):
        for check in node.checks:
            if check.id == 'service:foo':
                assert check.status == 'passing'

    for node in (yield from client.health.service('bar', state='any')):
        for check in node.checks:
            if check.id == 'service:bar':
                assert check.status == 'warning'

    for node in (yield from client.health.service('baz', state='any')):
        for check in node.checks:
            if check.id == 'service:baz':
                assert check.status == 'critical'

    # passing only

    for node in (yield from client.health.service('foo', state='passing')):
        for check in node.checks:
            assert check.status == 'passing'

    for node in (yield from client.health.service('bar', state='passing')):
        for check in node.checks:
            assert check.status == 'warning'

    for node in (yield from client.health.service('baz', state='passing')):
        for check in node.checks:
            assert check.status == 'critical'

    for check in (yield from client.health.state('passing')):
        assert check.status == 'passing'

    for check in (yield from client.health.state('warning')):
        assert check.status == 'warning'

    for check in (yield from client.health.state('critical')):
        assert check.status == 'critical'
