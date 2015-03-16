import asyncio
import logging
from aioconsul import Consul
from functools import wraps

logger = logging.getLogger(__name__)

# start a local agent for testing
# consul agent -config-file=tests/consul-agent.json


def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


@async_test
def test_kv_no_lock():
    client = Consul()

    try:
        value = yield from client.kv.get('foo')
    except client.kv.NotFound:
        logger.info('it was not found, it is OK')
    else:
        logger.info('was found! check now')
        assert value == 'bar'
        assert value.consul.key == 'foo'

    setted = yield from client.kv.set('foo', 'bar')
    assert setted

    value = yield from client.kv.get('foo')
    assert value == 'bar', value

    deleted = yield from client.kv.delete('foo')
    assert deleted, deleted
