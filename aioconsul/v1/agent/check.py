import asyncio
import json
import logging
from aioconsul.util import extract_id

logger = logging.getLogger(__name__)


class AgentCheckEndpoint:

    class NotFound(ValueError):
        pass

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def items(self):
        response = yield from self.client.get('/agent/checks')
        items = yield from response.json()
        logger.info('/agent/checks %s', items)
        return [decode(item) for item in items.values()]

    @asyncio.coroutine
    def register_script(self, name, script, *, interval, id=None, notes=None):
        response = yield from self.register(id=id,
                                            name=name,
                                            notes=notes,
                                            interval=interval,
                                            script=script)
        return response

    @asyncio.coroutine
    def register_http(self, name, http, *, interval, id=None, notes=None):
        response = yield from self.register(id=id,
                                            name=name,
                                            notes=notes,
                                            interval=interval,
                                            http=http)
        return response

    @asyncio.coroutine
    def register_ttl(self, name, ttl, *, id=None, notes=None):
        response = yield from self.register(id=id,
                                            name=name,
                                            notes=notes,
                                            ttl=ttl)
        return response

    @asyncio.coroutine
    def register(self, name, **params):
        path = '/agent/check/register'
        fields = [
            ('id', 'ID'),
            ('notes', 'Notes'),
            ('http', 'HTTP'),
            ('script', 'Script'),
            ('ttl', 'TTL'),
            ('interval', 'Interval'),
        ]
        data = {
            'Name': name
        }
        for a, b in fields:
            value = params.get(a, None)
            if value is not None:
                data[b] = value
        response = yield from self.client.put(path, data=json.dumps(data))
        if response.status == 200:
            return Check(id=params.get('id', name), name=name)

    @asyncio.coroutine
    def deregister(self, check):
        path = '/agent/check/deregister/%s' % extract_id(check)
        response = yield from self.client.get(path)
        return response.status == 200

    @asyncio.coroutine
    def passing(self, check, note=None):
        path = '/agent/check/pass/%s' % extract_id(check)
        response = yield from self.client.get(path, params={'note': note})
        return response.status == 200

    @asyncio.coroutine
    def warning(self, check, note=None):
        path = '/agent/check/warn/%s' % extract_id(check)
        response = yield from self.client.get(path, params={'note': note})
        return response.status == 200

    @asyncio.coroutine
    def failing(self, check, note=None):
        path = '/agent/check/fail/%s' % extract_id(check)
        response = yield from self.client.get(path, params={'note': note})
        return response.status == 200

    @asyncio.coroutine
    def get(self, check):
        response = yield from self.client.get('/agent/checks')
        items = yield from response.json()
        check_id = extract_id(check)
        logger.info('look for %s from %s', check_id, items)
        try:
            return decode(items[check_id])
        except KeyError:
            raise self.NotFound('Check %r was not found' % check_id)

    create = register
    delete = deregister


class Check:
    def __init__(self, id, *, name=None, node=None, notes=None, output=None,
                 service_id=None, service_name=None, status=None):
        self.id = id
        self.name = name
        self.node = node
        self.notes = notes
        self.output = output
        self.service_id = service_id
        self.service_name = service_name
        self.status = status

    def __repr__(self):
        return '<Check(id=%r, name=%r)>' % (self.id, self.name)


def decode(item):
    params = {}
    params['id'] = item.pop('CheckID', None)
    params['name'] = item.pop('Name', None)
    params['node'] = item.pop('Node', None)
    params['notes'] = item.pop('Notes', None)
    params['output'] = item.pop('Output', None)
    params['service_id'] = item.pop('ServiceID', None)
    params['service_name'] = item.pop('ServiceName', None)
    params['status'] = item.pop('Status', None)
    if item:
        logger.warn('These were not decoded %s', item)
    return Check(**params)
