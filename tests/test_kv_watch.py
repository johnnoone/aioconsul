import asyncio
import pytest
from aioconsul import Consul
from conftest import async_test


class Hold:

    def __init__(self, fut):
        self.response = None
        self.exception = None
        fut.add_done_callback(self)
    
    def __call__(self, response):
        try:
            self.response = response.result()
        except Exception as error:
            self.exception = error


@async_test
def test_key_1():
    client = Consul()
    yield from client.kv.set('foo', 'bar')
    loop = asyncio.get_event_loop()
    fut = client.kv.watch('foo')
    hold = Hold(fut)
    yield from client.kv.set('foo', 'baz')
    yield from asyncio.wait_for(fut, timeout=30)
    assert hold.response == 'baz'


@async_test
def test_key_2():
    client = Consul()
    fut = client.kv.watch('foo')
    hold = Hold(fut)
    yield from client.kv.set('foo', 'bar')
    yield from asyncio.wait_for(fut, timeout=30)
    assert hold.response == 'bar'


@async_test
def test_key_3():
    client = Consul()
    fut = client.kv.watch('foo')
    yield from client.kv.set('foo', 'bar')
    hold = Hold(fut)
    yield from asyncio.wait_for(fut, timeout=30)
    assert hold.response == 'bar'


@async_test
def test_key_4():
    client = Consul()
    fut = client.kv.watch('foo')
    hold = Hold(fut)
    yield from asyncio.wait([asyncio.async(client.kv.set('foo', 'bar')), fut],
                            timeout=30)
    assert hold.response == 'bar'


@async_test
def test_key_5():
    client = Consul()
    yield from client.kv.set('foo', 'bar')
    fut = client.kv.watch('foo')
    hold = Hold(fut)
    yield from asyncio.wait([asyncio.async(client.kv.set('foo', 'baz')), fut],
                            timeout=30)
    assert hold.response == 'baz'


@async_test
def test_key_6():
    client = Consul()
    yield from client.kv.set('foo', 'bar')
    fut = client.kv.watch('foo')
    hold = Hold(fut)
    yield from asyncio.wait([asyncio.async(client.kv.delete('foo')), fut],
                            timeout=30)
    assert isinstance(hold.exception, client.kv.NotFound)
