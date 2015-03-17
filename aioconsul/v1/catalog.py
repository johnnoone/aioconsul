import asyncio
import logging

log = logging.getLogger(__name__)


class CatalogEndpoint(object):

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def register(self, node, address, *, dc=None, check=None, service=None):
        raise NotImplementedError()

    @asyncio.coroutine
    def deregister(self):
        raise NotImplementedError()

    @asyncio.coroutine
    def datacenters(self):
        response = yield from self.client.get('/catalog/datacenters')
        return (yield from response.json())

    @asyncio.coroutine
    def nodes(self, *, dc=None):
        params = {'dc': dc}
        response = yield from self.client.get('/catalog/nodes',
                                              params=params)
        return (yield from response.json())

    @asyncio.coroutine
    def services(self, *, dc=None):
        params = {'dc': dc}
        response = yield from self.client.get('/catalog/services',
                                              params=params)
        return (yield from response.json())

    @asyncio.coroutine
    def node(self, name, *, dc=None):
        path = '/catalog/node/%s' % name
        params = {'dc': dc}
        response = yield from self.client.get(path, params=params)
        return (yield from response.json())

    @asyncio.coroutine
    def service(self, name, *, dc=None):
        path = '/catalog/service/%s' % name
        params = {'dc': dc}
        response = yield from self.client.get(path, params=params)
        return (yield from response.json())
