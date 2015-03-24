import asyncio
import logging
from aioconsul.bases import Node, NodeService, Check
from aioconsul.constants import CHECK_STATES
from aioconsul.exceptions import ValidationError
from aioconsul.response import render
from aioconsul.util import extract_id
logger = logging.getLogger(__name__)


class HealthEndpoint:

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def nodes(self, service, *, dc=None, tag=None, state=None):
        """Returns nodes by service, tag and state.

        The returned :class:`Node` instance has two special attributes:

        * `service` which holds an instance of :class:`NodeService`
        * `checks` which holds instances of :class:`Check`

        Parameters:
            service (Service): service or id
            dc (str): datacenter name
            tag (str): service tag
            state (str): ``passing`` or ``any``
        Returns:
            DataSet: set of :class:`Node` instances
        """
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
        values = set()
        for data in (yield from response.json()):
            node = Node(name=data['Node']['Node'],
                        address=data['Node']['Address'])
            node.service = NodeService(id=data['Service']['ID'],
                                       name=data['Service']['Service'],
                                       tags=data['Service']['Tags'],
                                       address=data['Service']['Address'],
                                       port=data['Service']['Port'])
            node.checks = [decode(chk) for chk in data['Checks']]
            values.add(node)
        return render(values, response=response)

    @asyncio.coroutine
    def items(self, *, node=None, service=None, state=None, dc=None):
        """Returns checks filtered by node, service and state.

        Parameters:
            node (Node): node or id
            service (Service): service or id
            state (str): check state
            dc (str): datacenter name
        Returns:
            DataSet: set of :class:`Check` instances
        Raises:
            ValidationError: an error occured
        """
        if node:
            path = '/health/node/%s' % extract_id(node)
            node = None
        elif service:
            path = '/health/checks/%s' % extract_id(service)
            service = None
        elif state:
            if state not in CHECK_STATES:
                raise ValidationError('Wrong state %r' % state)
            path = '/health/state/%s' % state
            state = None
        else:
            raise ValidationError('Required node, service or state')
        params = {'dc': dc}

        response = yield from self.client.get(path, params=params)
        values = {decode(data) for data in (yield from response.json())}
        if service:

            def filter_service(checks, service):
                service = extract_id(service)
                for check in checks:
                    if check.service_id == service:
                        yield check
            values = filter_service(values, service)
        if state:
            def filter_state(checks, state):
                if state not in CHECK_STATES:
                    raise ValidationError('Wrong state %r' % state)
                for check in checks:
                    if check.status == state:
                        yield check
            values = filter_state(values, state)
        return render(values, response=response)


def decode(data):
    return Check(id=data.get('CheckID'),
                 name=data.get('Name'),
                 status=data.get('Status'),
                 notes=data.get('Notes'),
                 output=data.get('Output'),
                 service_id=data.get('ServiceID'),
                 service_name=data.get('ServiceName'),
                 node=data.get('Node'))
