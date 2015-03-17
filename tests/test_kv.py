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
    for key in (yield from client.kv.keys('')):
        yield from client.kv.delete(key)


@async_test
def test_kv_no_lock():
    client = Consul()

    with pytest.raises(client.kv.NotFound):
        value = yield from client.kv.get('foo')

    setted = yield from client.kv.set('foo', 'bar')
    assert setted

    value = yield from client.kv.get('foo')
    assert value == 'bar', value

    deleted = yield from client.kv.delete('foo')
    assert deleted, deleted


@async_test
def test_bunch():
    client = Consul()
    keys = {'foo', 'bar', 'baz', 'quux'}
    for key in keys:
        setted = yield from client.kv.set(key, 'yup')
    found = yield from client.kv.keys('')
    assert keys == found
