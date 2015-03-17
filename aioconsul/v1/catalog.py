import asyncio
import logging
from aioconsul.bases import Node, NodeService
from aioconsul.exceptions import ValidationError
from aioconsul.util import extract_id

log = logging.getLogger(__name__)


class CatalogEndpoint:

    class NotFound(ValueError):
        pass

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
    def nodes(self, *, dc=None, service=None, tag=None):
        if service is not None:
            path = '/catalog/service/%s' % extract_id(service)
            params = {'dc': dc, 'tag': tag}
            response = yield from self.client.get(path, params=params)
            nodes = []
            for data in (yield from response.json()):
                node = Node(name=data.get('Node'),
                            address=data.get('Address'))
                node.service = NodeService(id=data.get('ServiceID'),
                                           name=data.get('ServiceName'),
                                           tags=data.get('ServiceTags'),
                                           address=data.get('ServiceAddress'),
                                           port=data.get('ServicePort'))
                nodes.append(node)
            return nodes

        elif tag is not None:
            raise ValidationError('Tag belongs to service')

        else:
            path = '/catalog/nodes'
            params = {'dc': dc}
            response = yield from self.client.get(path, params=params)
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
            node = Node(data['Node'].get('Node'),
                        data['Node'].get('Address'))
            node.services = {}
            for k, d in data['Services'].items():
                node.services[k] = NodeService(id=d.get('ID'),
                                               name=d.get('Service'),
                                               tags=d.get('Tags'),
                                               port=d.get('Port'))
            return node
        raise self.NotFound('No node was not found for %s' % name)

    @asyncio.coroutine
    def services(self, *, dc=None):
        params = {'dc': dc}
        response = yield from self.client.get('/catalog/services',
                                              params=params)
        return (yield from response.json())
