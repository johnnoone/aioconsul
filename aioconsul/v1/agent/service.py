import asyncio
import json
import logging
from aioconsul.bases import NodeService
from aioconsul.exceptions import HTTPError, ValidationError
from aioconsul.util import extract_id

logger = logging.getLogger(__name__)


class AgentServiceEndpoint:

    class NotFound(ValueError):
        """Raised when service was not found"""

    def __init__(self, client, *, loop=None):
        self.client = client
        self.loop = loop or asyncio.get_event_loop()

    @asyncio.coroutine
    def items(self):
        """Returns the services the local agent is managing.

        Returns:
            set: set of :class:`Check` instances
        """
        response = yield from self.client.get('/agent/services')
        items = yield from response.json()
        return [decode(item) for item in items.values()]

    __call__ = items

    @asyncio.coroutine
    def register_script(self, name, script, *, id=None, tags=None,
                        address=None, port=None, interval=None):
        """Registers a new local service with a check by script.

        Parameters:
            name (str): service name
            script (str): path to script
            interval (str): evaluate script every `ìnterval`
            id (str): service id
            tags (list): service tags
            address (str): service address
            port (str): service port
        Returns:
             NodeService: instance
        """
        response = yield from self.register(id=id,
                                            name=name,
                                            tags=tags,
                                            address=address,
                                            port=port,
                                            check=dict(script=script,
                                                       interval=interval))
        return response

    @asyncio.coroutine
    def register_http(self, name, http, *, id=None, tags=None,
                      address=None, port=None, interval=None):
        """Registers a new local service with a check by http.

        Parameters:
            name (str): service name
            http (str): url to ping
            interval (str): evaluate script every `ìnterval`
            id (str): service id
            tags (list): service tags
            address (str): service address
            port (str): service port
        Returns:
             NodeService: instance
        """
        response = yield from self.register(id=id,
                                            name=name,
                                            tags=tags,
                                            address=address,
                                            port=port,
                                            check=dict(http=http,
                                                       interval=interval))
        return response

    @asyncio.coroutine
    def register_ttl(self, name, ttl, *, id=None,
                     tags=None, address=None, port=None):
        """Registers a new local service with a check by ttl.

        Parameters:
            name (str): service name
            ttl (str): period status update
            id (str): service id
            tags (list): service tags
            address (str): service address
            port (str): service port
        Returns:
             NodeService: instance
        """
        response = yield from self.register(id=id,
                                            name=name,
                                            tags=tags,
                                            address=address,
                                            port=port,
                                            check=dict(ttl=ttl))
        return response

    @asyncio.coroutine
    def register(self, name, *, id=None, tags=None,
                 address=None, port=None, check=None):
        """Registers a new local service.

        Parameters:
            name (str): service name
            id (str): service id
            tags (list): service tags
            address (str): service address
            port (str): service port
        Returns:
             NodeService: instance
        """
        path = '/agent/service/register'
        data = {
            'Name': name
        }
        if id:
            data['ID'] = id
        if tags:
            data['Tags'] = tags
        if address:
            data['Address'] = address
        if port:
            data['Port'] = port
        if check:
            c = data['Check'] = {}
            if 'script' in check:
                c['Script'] = check['script']
            elif 'http' in check:
                c['HTTP'] = check['http']
            elif 'ttl' in check:
                c['TTL'] = check['ttl']
            else:
                raise ValueError('script, http or ttl are mandatory')
            if 'interval' in check:
                c['Interval'] = check['interval']
            elif 'Script' in c or 'HTTP' in c:
                raise ValidationError('Interval is mandatory')

        response = yield from self.client.put(path, data=json.dumps(data))
        if response.status == 200:
            return NodeService(id=id or name,
                               name=name,
                               tags=tags,
                               address=address,
                               port=port)
        msg = yield from response.text()
        if response.status == 400:
            raise ValidationError(msg)
        raise HTTPError(msg, response.status)

    @asyncio.coroutine
    def deregister(self, service):
        """Deregister a local service.

        Parameters:
            service (NodeService): service or id
        Returns:
             bool: ``True`` it has been deregistered
        """
        path = '/agent/service/deregister/%s' % extract_id(service)
        response = yield from self.client.get(path)
        return response.status == 200

    @asyncio.coroutine
    def enable(self, service, reason=None):
        """Enable service.

        Parameters:
            service (NodeService): service or id
            reason (str): human readable reason
        Returns:
             bool: ``True`` it has been enabled
        """
        response = yield from self.maintenance(service, False, reason)
        return response

    @asyncio.coroutine
    def disable(self, service, reason=None):
        """Disable service.

        Parameters:
            service (NodeService): service or id
            reason (str): human readable reason
        Returns:
             bool: ``True`` it has been disabled
        """
        response = yield from self.maintenance(service, True, reason)
        return response

    @asyncio.coroutine
    def maintenance(self, service, enable, reason=None):
        """Manages service maintenance mode.

        Parameters:
            service (NodeService): service or id
            enable (bool): in maintenance or not
            reason (str): human readable reason
        Returns:
             bool: ``True`` all is OK
        """
        path = '/agent/service/maintenance/%s' % extract_id(service)
        params = {
            'enable': enable,
            'reason': reason
        }
        response = yield from self.client.get(path, params=params)
        return response.status == 200

    @asyncio.coroutine
    def get(self, service):
        """Fetch local service.

        Parameters:
            service (NodeService): service or id
        Returns:
            Service: instance
        Raises:
            NotFound: service was not found
        """
        response = yield from self.client.get('/agent/services')
        items = yield from response.json()
        service_id = extract_id(service)
        try:
            return decode(items[service_id])
        except KeyError:
            raise self.NotFound('Service %r was not found' % service_id)

    create = register
    delete = deregister


def decode(data):
    return NodeService(id=data.get('ID'),
                       name=data.get('Service'),
                       address=data.get('Address'),
                       port=data.get('Port'),
                       tags=data.get('Tags'))
