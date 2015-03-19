import pytest
from aioconsul import Consul
from conftest import async_test


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
    keys = {'foo', 'bar', 'baz', 'quux', '1/2'}
    for key in keys:
        yield from client.kv.set(key, 'yup')
    found = yield from client.kv.keys('', separator='/')
    assert {'foo', 'bar', 'baz', 'quux', '1/'} == found

    data = yield from client.kv.items('1')
    assert data == {'1/2': 'yup'}
