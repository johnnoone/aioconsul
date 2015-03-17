import asyncio
import json
import logging
from aioconsul.exceptions import HTTPError, ValidationError
from aioconsul.util import extract_id

logger = logging.getLogger(__name__)


class AgentServiceEndpoint(object):

    class NotFound(ValueError):
        pass

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def items(self):
        response = yield from self.client.get('/agent/services')
        items = yield from response.json()
        return [decode(item) for item in items.values()]

    @asyncio.coroutine
    def register_script(self, name, script, *, id=None, tags=None,
                        address=None, port=None, interval=None):
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
        response = yield from self.register(id=id,
                                            name=name,
                                            tags=tags,
                                            address=address,
                                            port=port,
                                            check=dict(http=http,
                                                       interval=interval))
        return response

    @asyncio.coroutine
    def register_ttl(self, name, ttl, *, id=None, tags=None,
                     address=None, port=None, interval=None):
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

        try:
            response = yield from self.client.put(path, data=json.dumps(data))
            if response.status == 200:
                return Service(id=id or name,
                               name=name,
                               tags=tags,
                               address=address,
                               port=port)
        except HTTPError as error:
            if error.status == 400:
                raise ValidationError(str(error))
            raise

    @asyncio.coroutine
    def deregister(self, service):
        path = '/agent/service/deregister/%s' % extract_id(service)
        response = yield from self.client.get(path)
        return response.status == 200

    @asyncio.coroutine
    def maintenance(self, service, enable, reason=None):
        path = '/agent/service/maintenance/%s' % extract_id(service)
        params = {
            'enable': enable,
            'reason': reason
        }
        response = yield from self.client.get(path, params=params)
        return response.status == 200

    @asyncio.coroutine
    def get(self, service):
        response = yield from self.client.get('/agent/services')
        items = yield from response.json()
        service_id = extract_id(service)
        try:
            return decode(items[service_id])
        except KeyError:
            raise self.NotFound('Service %r was not found' % service_id)

    create = register
    delete = deregister


class Service:
    def __init__(self, id, name, *, address=None, port=None, tags=None):
        self.id = id
        self.name = name
        self.address = address
        self.port = port
        self.tags = tags

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<Service(id=%r)>' % self.id


def decode(data):
    params = {}
    params['id'] = data.pop('ID', None)
    params['name'] = data.pop('Service', None)
    params['address'] = data.pop('Address', None)
    params['port'] = data.pop('Port', None)
    params['tags'] = data.pop('Tags', None)
    if data:
        logger.warn('These were not decoded %r', data)
    return Service(**params)
