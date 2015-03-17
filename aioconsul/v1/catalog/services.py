import asyncio
import logging

log = logging.getLogger(__name__)


class CatalogServiceEndpoint:

    class NotFound(ValueError):
        pass

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def items(self, *, dc=None):
        params = {'dc': dc}
        response = yield from self.client.get('/catalog/services',
                                              params=params)
        return (yield from response.json())

    @asyncio.coroutine
    def get(self, id, *, dc=None, tag=None):
        path = '/catalog/service/%s' % id
        params = {'dc': dc, 'tag': tag}
        response = yield from self.client.get(path, params=params)
        data = (yield from response.json())
        if data:
            return NodeSet(id, decode(data))
        raise self.NotFound('No node with %s was not found' % id)


class NodeSet:
    def __init__(self, service, nodes):
        self.service = service
        self.nodes = nodes

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)
    
    def __repr__(self):
        return '<NodeSet(service=%r)>' % self.service


class Node:
    def __init__(self, name, *, address, service):
        self.name = name
        self.address = address
        self.service = service
    
    def __repr__(self):
        return '<Node(name=%r)>' % self.name


class NodeService:
    def __init__(self, id, *, name, tags, address, port):
        self.id = id
        self.name = name
        self.tags = tags
        self.address = address
        self.port = port
    
    def __repr__(self):
        return '<NodeService(id=%r)>' % self.id


def decode(data):
    nodes = []

    for d in data:
        node_params = {
            'name': d.pop('Node', None),
            'address': d.pop('Address', None),
        }
        service_params = {
            'id': d.pop('ServiceID', None),
            'name': d.pop('ServiceName', None),
            'tags': d.pop('ServiceTags', None),
            'address': d.pop('ServiceAddress', None),
            'port': d.pop('ServicePort', None),
        }
        if d:
            logger.warn('No used %s', d)
        srv = NodeService(**service_params)
        node = Node(service=srv, **node_params)
        nodes.append(node)
    return nodes
