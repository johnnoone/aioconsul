import asyncio
import pytest
from aioconsul import Consul, ValidationError
from conftest import async_test


@async_test
def test_health():
    client = Consul()

    for check in (yield from client.health.items(node='my-local-node')):
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

    for check in (yield from client.health.items(service='serfHealth')):
        assert check.status == 'passing'

    # test nodes

    for node in (yield from client.health.nodes(service='foo')):
        for check in node.checks:
            if check.id == 'service:foo':
                assert check.status == 'passing'

    for node in (yield from client.health.nodes(service='bar')):
        for check in node.checks:
            if check.id == 'service:bar':
                assert check.status == 'warning'

    for node in (yield from client.health.nodes(service='baz')):
        for check in node.checks:
            if check.id == 'service:baz':
                assert check.status == 'critical'

    # passing only

    for node in (yield from client.health.nodes(service='foo', state='passing')):
        for check in node.checks:
            assert check.status == 'passing'
        for service in node:
            assert service.name == 'foo'

    for node in (yield from client.health.nodes(service='bar', state='passing')):
        for check in node.checks:
            assert check.status == 'warning'
        for service in node:
            assert service.name == 'bar'

    for node in (yield from client.health.nodes(service='baz', state='passing')):
        for check in node.checks:
            assert check.status == 'critical'
        for service in node:
            assert service.name == 'baz'

    for check in (yield from client.health.items(state='passing')):
        assert check.status == 'passing'

    for check in (yield from client.health.items(state='warning')):
        assert check.status == 'warning'

    for check in (yield from client.health.items(state='critical')):
        assert check.status == 'critical'

    # mixing checks
    with pytest.raises(ValidationError):
        yield from client.health.items()  # node, service or state required

    for check in (yield from client.health.items(node='my-local-node', state='passing')):
        assert check.status == 'passing'

    for check in (yield from client.health.items(node='my-local-node', service='foo')):
        assert check.status == 'passing'

    for check in (yield from client.health.items(node='my-local-node', service='bar')):
        assert check.status == 'warning'

    for check in (yield from client.health.items(node='my-local-node', service='baz')):
        assert check.status == 'critical'
