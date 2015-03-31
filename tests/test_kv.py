import asyncio
import functools
import logging
import pytest
from aioconsul import Consul
from conftest import async_test

logger = logging.getLogger(__name__)

@async_test
def test_simple():
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


@async_test
def test_inexistant_watch_sync():
    # synchrone test
    client = Consul()

    meta = yield from client.kv.meta('batang')
    task = client.kv.get('batang', watch=meta)
    yield from client.kv.set('batang', 'sichuan')
    yield from asyncio.wait_for(task, timeout=10)
    assert task.result() == 'sichuan', task


@async_test
def test_inexistant_watch_async():
    # async test
    client = Consul()

    def res_handler(src, *, next):
        next.set_result('%sy elliot' % src.result())

    def watch_handler(src, *, next):
        meta = src.result()
        task = client.kv.get('boule', watch=meta)
        task.add_done_callback(functools.partial(res_handler, next=next))

    step2 = asyncio.Future()

    step1 = client.kv.meta('boule')
    step1.add_done_callback(functools.partial(watch_handler, next=step2))
    yield from client.kv.set('boule', 'bill')
    yield from asyncio.wait_for(step2, timeout=10)
    assert step2.result() == 'billy elliot', step2


@async_test
def test_bunch_watch_sync():
    client = Consul()

    # synchrone
    meta = yield from client.kv.meta(prefix='pref/')
    task = client.kv.items('pref/', watch=meta)
    yield from client.kv.set('pref/batang', 'sichuan')
    yield from asyncio.wait_for(task, timeout=10)
    assert task.result()['pref/batang'] == 'sichuan', task


@async_test
def test_bunch_watch_async():
    client = Consul()

    def res_handler(src, *, next):
        next.set_result(src.result())

    def watch_handler(src, *, next):
        meta = src.result()
        task = client.kv.items('pokemon/', watch=meta)
        task.add_done_callback(functools.partial(res_handler, next=next))

    step2 = asyncio.Future()

    step1 = client.kv.meta(prefix='pokemon/')
    step1.add_done_callback(functools.partial(watch_handler, next=step2))
    yield from client.kv.set('pokemon/pika', 'chu')
    yield from asyncio.wait_for(step2, timeout=10)
    assert step2.result()['pokemon/pika'] == 'chu', step2
