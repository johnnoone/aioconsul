import asyncio
import logging
from aioconsul.bases import Node, NodeService, Check
from aioconsul.constants import CHECK_STATES
from aioconsul.exceptions import ValidationError
from aioconsul.util import extract_id
logger = logging.getLogger(__name__)


class HealthEndpoint:

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def node(self, node, *, dc=None):
        path = '/health/node/%s' % extract_id(node)
        params = {'dc': dc}
        response = yield from self.client.get(path, params=params)
        return {decode(data) for data in (yield from response.json())}

    @asyncio.coroutine
    def checks(self, service, *, dc=None):
        path = '/health/checks/%s' % extract_id(service)
        params = {'dc': dc}
        response = yield from self.client.get(path, params=params)
        return {decode(data) for data in (yield from response.json())}

    @asyncio.coroutine
    def service(self, service, *, dc=None, tag=None, state=None):
        path = '/health/service/%s' % extract_id(service)
        params = {'dc': dc,
                  'tag': tag}
        if state == 'passing':
            params['passing'] = True
        elif state == 'any':
            pass
        elif state:
            raise ValidationError('State must be passing')
        response = yield from self.client.get(path, params=params)
        nodes = set()
        for data in (yield from response.json()):
            node = Node(name=data['Node']['Node'],
                        address=data['Node']['Address'])
            node.service = NodeService(id=data['Service']['ID'],
                                       name=data['Service']['Service'],
                                       tags=data['Service']['Tags'],
                                       address=data['Service']['Address'],
                                       port=data['Service']['Port'])
            node.checks = [decode(chk) for chk in data['Checks']]
            nodes.add(node)
        return nodes

    @asyncio.coroutine
    def state(self, state, *, dc=None):
        if state not in CHECK_STATES:
            raise ValidationError('Wrong state %r' % state)
        path = '/health/state/%s' % state
        params = {'dc': dc}
        response = yield from self.client.get(path, params=params)
        return {decode(data) for data in (yield from response.json())}


def decode(data):
    return Check(id=data.get('CheckID'),
                 name=data.get('Name'),
                 status=data.get('Status'),
                 notes=data.get('Notes'),
                 output=data.get('Output'),
                 service_id=data.get('ServiceID'),
                 service_name=data.get('ServiceName'),
                 node=data.get('Node'))
