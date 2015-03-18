import asyncio
import json
from aioconsul.bases import Check
from aioconsul.util import extract_id


class AgentCheckEndpoint:

    class NotFound(ValueError):
        pass

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def items(self):
        response = yield from self.client.get('/agent/checks')
        items = yield from response.json()
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
        response = yield from self.mark(check, 'passing', note=note)
        return response

    @asyncio.coroutine
    def warning(self, check, note=None):
        response = yield from self.mark(check, 'warning', note=note)
        return response

    @asyncio.coroutine
    def failing(self, check, note=None):
        response = yield from self.mark(check, 'critical', note=note)
        return response

    @asyncio.coroutine
    def mark(self, check, state, *, note=None):
        route = {'passing': 'pass',
                 'warning': 'warn',
                 'failing': 'fail',
                 'critical': 'fail'}.get(state, state)
        path = '/agent/check/%s/%s' % (route, extract_id(check))
        response = yield from self.client.get(path, params={'note': note})
        return response.status == 200

    @asyncio.coroutine
    def get(self, check):
        response = yield from self.client.get('/agent/checks')
        items = yield from response.json()
        check_id = extract_id(check)
        try:
            return decode(items[check_id])
        except KeyError:
            raise self.NotFound('Check %r was not found' % check_id)

    create = register
    delete = deregister


def decode(data):
    return Check(id=data.get('CheckID'),
                 name=data.get('Name'),
                 status=data.get('Status'),
                 notes=data.get('Notes'),
                 output=data.get('Output'),
                 service_id=data.get('ServiceID'),
                 service_name=data.get('ServiceName'),
                 node=data.get('Node'))
