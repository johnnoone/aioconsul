import asyncio
import logging

log = logging.getLogger(__name__)


class CatalogNodeEndpoint:

    class NotFound(ValueError):
        pass

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def items(self, *, dc=None):
        params = {'dc': dc}
        response = yield from self.client.get('/catalog/nodes',
                                              params=params)
        nodes = []
        for data in (yield from response.json()):
            node = Node(data.get('Node'), data.get('Address'))
            nodes.append(node)
        return nodes

    @asyncio.coroutine
    def get(self, name, *, dc=None):
        path = '/catalog/node/%s' % name
        params = {'dc': dc}
        response = yield from self.client.get(path, params=params)
        data = (yield from response.json())
        if data:
            services = {}
            for k, d in data['Services'].items():
                services[k] = Service(id=d.get('ID'),
                                      name=d.get('Service'),
                                      tags=d.get('Tags'),
                                      port=d.get('Port'))
            return Node(data['Node'].get('Node'),
                        address=data['Node'].get('Address'),
                        services=services)
        raise self.NotFound('No node was not found for %s' % name)


class Node:
    def __init__(self, name, address, *, services=None):
        self.name = name
        self.address = address
        if services:
            self.services = services

    def __repr__(self):
        return '<Node(name=%r)>' % self.name


class Service:
    def __init__(self, id, *, name, tags, port):
        self.id = id
        self.name = name
        self.tags = tags
        self.port = port

    def __repr__(self):
        return '<Node(id=%r)>' % self.id
