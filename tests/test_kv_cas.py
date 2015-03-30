import pytest
from aioconsul import Consul
from conftest import async_test

# TODO test CAS

@async_test
def test_cas():
    client = Consul()

    with pytest.raises(client.kv.NotFound):
        value = yield from client.kv.get('foo')

    setted = yield from client.kv.set('foo', 'bar', cas=0)
    assert setted

    value = yield from client.kv.get('foo')
    assert value == 'bar'

    # test put with cas

    setted = yield from client.kv.set('foo', 'baz', cas=42)
    assert not setted

    value = yield from client.kv.get('foo')
    assert value == 'bar'

    setted = yield from client.kv.set('foo', 'baz', cas=value.consul)
    assert setted

    value = yield from client.kv.get('foo')
    assert value == 'baz'

    # test delete with cas

    deleted = yield from client.kv.delete('foo', cas=42)
    assert not deleted

    deleted = yield from client.kv.delete('foo', cas=value.consul)
    assert deleted

    with pytest.raises(client.kv.NotFound):
        value = yield from client.kv.get('foo')
