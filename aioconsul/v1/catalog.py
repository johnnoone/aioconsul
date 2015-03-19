import asyncio
import json
import logging
from aioconsul.bases import Check, Node, NodeService, Service
from aioconsul.exceptions import ValidationError
from aioconsul.util import extract_id

log = logging.getLogger(__name__)


class CatalogEndpoint:

    class NotFound(ValueError):
        """Raised when a node was not found."""
        pass

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def register_node(self, node, *, dc=None):
        """Registers a node"""
        response = yield from self.register(node, dc=dc)
        return response

    @asyncio.coroutine
    def register_check(self, node, *, check, dc=None):
        """Registers a check"""
        response = yield from self.register(node, check=check, dc=dc)
        return response

    @asyncio.coroutine
    def register_service(self, node, *, service, dc=None):
        """Registers a service"""
        response = yield from self.register(node, service=service, dc=dc)
        return response

    @asyncio.coroutine
    def register(self, node, *, dc=None, check=None, service=None):
        """Registers to catalog"""
        path = 'catalog/register'

        def conf(data):
            return {k: v for k, v in data.items() if v is not None}

        if isinstance(node, dict):
            node = Node(name=node.get('name'),
                        address=node.get('address'))

        if isinstance(check, dict):
            check = Check(id=check.get('id'),
                          name=check.get('name'),
                          status=check.get('status'),
                          notes=check.get('notes'),
                          output=check.get('output'),
                          service_id=check.get('service_id'),
                          service_name=check.get('service_name'),
                          node=check.get('node'))

        if isinstance(service, dict):
            service = NodeService(id=service.get('id'),
                                  name=service.get('name'),
                                  address=service.get('address'),
                                  port=service.get('port'),
                                  tags=service.get('tags'))

        data = conf({
            'Datacenter': dc,
            'Node': node.name,
            'Address': node.address
        })
        if service:
            data['Service'] = conf({
                'ID': service.id,
                'Service': service.name,
                'Address': service.address,
                'Port': service.port,
                'Tags': service.tags
            })

        if check:
            data['Check'] = conf({
                'CheckID': check.id,
                'Name': check.name,
                'Notes': check.notes,
                'Status': check.status,
                'Node': check.node or node.name,
                'ServiceID': check.service_id
            })
        response = yield from self.client.put(path, data=json.dumps(data))
        return response.status == 200

    @asyncio.coroutine
    def deregister_node(self, node, *, dc=None):
        """Deregisters a node"""
        response = yield from self.deregister(node, dc=dc)
        return response

    @asyncio.coroutine
    def deregister_check(self, node, *, check, dc=None):
        """Deregisters a check"""
        response = yield from self.deregister(node, dc=dc, check=check)
        return response

    @asyncio.coroutine
    def deregister_service(self, node, *, service, dc=None):
        """Deregisters a service"""
        response = yield from self.deregister(node, dc=dc, service=service)
        return response

    @asyncio.coroutine
    def deregister(self, node, *, check=None, service=None, dc=None):
        """Deregisters from catalog"""
        path = 'catalog/deregister'

        def conf(data):
            return {k: v for k, v in data.items() if v is not None}

        if isinstance(node, dict):
            node = node.get('name')
        elif isinstance(node, Node):
            node = node.name

        if isinstance(check, dict):
            check_id = check.get('id') or check.get('name')
        elif isinstance(check, Check):
            check_id = check.id or check.name
        else:
            check_id = check

        if isinstance(service, dict):
            service_id = service.get('id') or service.get('name')
        elif isinstance(service, Service):
            service_id = service.id or service.name
        else:
            service_id = service

        data = conf({
            'Datacenter': dc,
            'Node': node,
            'CheckID': check_id,
            'ServiceID': service_id
        })

        if service and ('ServiceID' not in data):
            raise ValidationError('Unable to define service')

        if check and ('CheckID' not in data):
            raise ValidationError('Unable to define check')

        response = yield from self.client.put(path, data=json.dumps(data))
        return response.status == 200

    @asyncio.coroutine
    def datacenters(self):
        """Lists datacenters

        :returns: a set of datacenters
        :rtype: set
        """
        response = yield from self.client.get('/catalog/datacenters')
        return set((yield from response.json()))

    @asyncio.coroutine
    def nodes(self, *, dc=None, service=None, tag=None):
        """Lists nodes.

        If service is given, node instances will have a special
        attribute named `service`, which implements a NodeService
        instance.
        """
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
        """Get a node. Raises a NotFound if it's not found.

        The instance will have a special attributes named `services`,
        which implements a list of services attached to the node.
        """
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
        """Lists services.

        :returns: a mapping of services - known tags
        :rtype: dict
        """
        params = {'dc': dc}
        response = yield from self.client.get('/catalog/services',
                                              params=params)
        return (yield from response.json())
