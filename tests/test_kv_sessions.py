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
def test_acquire():
    """Test ephemeral operations
    """

    master = Consul(consistency='consistent')
    client = Consul(consistency='consistent')

    session_a = yield from master.session.create(behavior='release')
    session_b = yield from master.session.create(behavior='release')

    tasks = []
    for key, value in fixtures.items():
        tasks.append(asyncio.async(master.kv.acquire(key, session=session_a)))
    done, pending = yield from asyncio.wait(tasks)
    for fut in done:
        assert fut.result()

    # can read keys
    keys = yield from client.kv.keys('')
    assert len(keys) == len(fixtures)

    # but cannot acquire them
    tasks = []
    for key, value in fixtures.items():
        tasks.append(asyncio.async(master.kv.acquire(key, session=session_b)))
    done, pending = yield from asyncio.wait(tasks)
    for fut in done:
        assert not fut.result()

    # release them
    tasks = []
    for key, value in fixtures.items():
        tasks.append(asyncio.async(master.kv.release(key, session=session_a)))
    done, pending = yield from asyncio.wait(tasks)
    for fut in done:
        assert fut.result()

    yield from client.session.delete(session_a)
    yield from client.session.delete(session_b)


@async_test
def test_ephemeral():
    """Test ephemeral operations
    """

    client = Consul(consistency='consistent')

    session = yield from client.session.create(behavior='delete')

    tasks = []
    for key in fixtures.keys():
        tasks.append(asyncio.async(client.kv.acquire(key, session=session)))
    done, pending = yield from asyncio.wait(tasks)
    for fut in done:
        assert fut.result()

    keys = yield from client.kv.keys('')
    assert len(keys) == len(fixtures)

    yield from client.session.delete(session)

    keys = yield from client.kv.keys('')
    assert len(keys) == 0
