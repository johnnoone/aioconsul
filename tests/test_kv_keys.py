import asyncio
from aioconsul import Consul
from conftest import async_test

fixtures = {
    'foo': 'bar',
    'foo/bar': 'baz',
    'foo/bar/baz': 'quux',
    'bar': 'baz',
    'bar/baz': 'quux',
    'baz': 'quux'
}


@async_test
def test_keys():
    """Test keys operations
    """

    master = Consul(consistency='consistent')
    client = Consul(consistency='consistent')

    keys = yield from client.kv.keys('')
    assert len(keys) == 0

    # create a bunch of keys
    tasks = []
    for key, value in fixtures.items():
        tasks.append(asyncio.async(client.kv.set(key, value)))
    done, pending = yield from asyncio.wait(tasks)
    for fut in done:
        assert fut.result()

    keys = yield from client.kv.keys('')
    for key in fixtures.keys():
        assert key in fixtures.keys()
    assert keys.modify_index

    keys = yield from client.kv.keys('b', separator='/')
    for key in keys:
        assert key in {'baz', 'bar', 'bar/'}
    assert keys.modify_index
