import asyncio
from aioconsul import Consul


def test_client():
    client = Consul('http://foo')
    assert client.host == 'http://foo'
    assert client.version == 'v1'


def test_low():
    client = Consul()

    @asyncio.coroutine
    def run(client, fut):
        response = yield from client.get('status/leader')
        fut.set_result((yield from response.json()))

    fut = asyncio.Future()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(client, fut))

    assert fut.result().endswith(':8300')
