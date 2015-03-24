import asyncio
import copy
import json
import logging
from aioconsul.bases import Check, Node, NodeService, Service
from aioconsul.exceptions import ValidationError
from aioconsul.response import render
from aioconsul.util import extract_id, extract_name

log = logging.getLogger(__name__)


class CatalogEndpoint:
    """
    Attributes:
        dc (str): the datacenter
    """

    class NotFound(ValueError):
        """Raised when a node was not found."""
        pass

    def __init__(self, client, dc=None):
        self.client = client
        self.dc = dc

    def dc(self, name):
        """
        Wraps requests to the specified datacenter.

        Parameters:
            name (str): datacenter name

        Returns:
            CatalogEndpoint: a new endpoint
        """
        instance = copy.copy(self)
        instance.dc = name
        return instance

    @asyncio.coroutine
    def register_node(self, node):
        """Registers a node"""
        response = yield from self.register(node)
        return response

    @asyncio.coroutine
    def register_check(self, node, *, check):
        """Registers a check"""
        response = yield from self.register(node, check=check)
        return response

    @asyncio.coroutine
    def register_service(self, node, *, service):
        """Registers a service"""
        response = yield from self.register(node, service=service)
        return response

    @asyncio.coroutine
    def register(self, node, *, check=None, service=None):
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
            'Datacenter': self.dc,
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
    def deregister_node(self, node):
        """Deregisters a node

        Parameters:
            node (Node): node or id
        Returns:
            bool: ``True`` it is deregistered
        Raises:
            ValidationError: an error occured
        """
        response = yield from self.deregister(node)
        return response

    @asyncio.coroutine
    def deregister_check(self, node, *, check):
        """Deregisters a check

        Parameters:
            node (Node): node or id
            check (Check): check or id
        Returns:
            bool: ``True`` it is deregistered
        Raises:
            ValidationError: an error occured
        """
        response = yield from self.deregister(node, check=check)
        return response

    @asyncio.coroutine
    def deregister_service(self, node, *, service):
        """Deregisters a service

        Parameters:
            node (Node): node or id
            service (NodeService): service or id
        Returns:
            bool: ``True`` it is deregistered
        Raises:
            ValidationError: an error occured
        """
        response = yield from self.deregister(node, service=service)
        return response

    @asyncio.coroutine
    def deregister(self, node, *, check=None, service=None):
        """Deregisters from catalog

        Parameters:
            node (Node): node or id
            check (Check): check or id
            service (NodeService): service or id
        Returns:
            bool: ``True`` it is deregistered
        Raises:
            ValidationError: an error occured
        """
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
            'Datacenter': self.dc,
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

        Returns:
            set: a set of datacenters
        """
        response = yield from self.client.get('/catalog/datacenters')
        return set((yield from response.json()))

    @asyncio.coroutine
    def nodes(self, *, service=None, tag=None):
        """Lists nodes.

        If service is given, :class:`Node` instances will have a special
        attribute named `service`, which holds a :class:`NodeService` instance.

        Parameters:
            service (Service): service or id
            tag (str): tag of service
        Returns:
            DataSet: set of :class:`Node` instances
        Raises:
            ValidationError: an error occured
        """
        if service is not None:
            path = '/catalog/service/%s' % extract_id(service)
            params = {'dc': self.dc, 'tag': tag}
            response = yield from self.client.get(path, params=params)
            values = []
            for data in (yield from response.json()):
                node = Node(name=data.get('Node'),
                            address=data.get('Address'))
                node.service = NodeService(id=data.get('ServiceID'),
                                           name=data.get('ServiceName'),
                                           tags=data.get('ServiceTags'),
                                           address=data.get('ServiceAddress'),
                                           port=data.get('ServicePort'))
                values.append(node)
            return render(values, response=response)

        elif tag is not None:
            raise ValidationError('Tag belongs to service')

        else:
            path = '/catalog/nodes'
            params = {'dc': self.dc}
            response = yield from self.client.get(path, params=params)
            values = []
            for data in (yield from response.json()):
                node = Node(name=data.get('Node'),
                            address=data.get('Address'))
                values.append(node)
            return render(values, response=response)

    @asyncio.coroutine
    def get(self, node):
        """Get a node. Raises a NotFound if it's not found.

        The returned :class:`Node` instance has a special attribute named
        `services` which holds a list of :class:`NodeService`.

        The returned objects has a special attribute named
        `services` which holds the :class:`Key` informations.

        Parameters:
            node (str): node or name
        Returns:
            Node: instance
        Raises:
            NotFound: node was not found
        """
        name = extract_name(node)
        path = '/catalog/node/%s' % extract_name(name)
        params = {'dc': self.dc}
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
    def services(self):
        """Lists services.

        Returns:
            dict: a mapping of services - known tags
        """
        params = {'dc': self.dc}
        response = yield from self.client.get('/catalog/services',
                                              params=params)
        values = yield from response.json()
        return render(values, response=response)
