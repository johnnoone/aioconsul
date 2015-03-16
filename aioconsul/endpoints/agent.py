import asyncio
import json
import logging
from aioconsul.util import extract_id

log = logging.getLogger(__name__)


class AgentEndpoint(object):
    def __init__(self, client):
        self.client = client
        self.checks = AgentCheckEndpoint(client)
        self.services = AgentServiceEndpoint(client)

    @asyncio.coroutine
    def members(self):
        response = yield from self.client.get('/agent/members')
        return (yield from response.json())

    @asyncio.coroutine
    def me(self):
        response = yield from self.client.get('/agent/self')
        return (yield from response.json())

    @asyncio.coroutine
    def maintenance(self, enable, reason=None):
        params = {
            'enable': enable,
            'reason': reason
        }
        response = yield from self.client.get('/agent/maintenance',
                                              params=params)
        return response.status == 200

    @asyncio.coroutine
    def join(self, address, *, wan=None):
        path = '/agent/join/%s' % str(address).lstrip('/')
        params = {}
        if wan:
            params['wan'] = 1
        response = yield from self.client.get(path, params=params)
        return response.status == 200

    @asyncio.coroutine
    def force_leave(self, node):
        path = '/agent/force-leave/%s' % str(node).lstrip('/')
        response = yield from self.client.get(path)
        return response.status == 200


class AgentCheckEndpoint(object):

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def items(self):
        response = yield from self.client.get('/agent/checks')
        return (yield from response.json())

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
        return response.status == 200

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


class AgentServiceEndpoint(object):

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def items(self):
        response = yield from self.client.get('/agent/services')
        return (yield from response.json())

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
        path = '/agent/check/register'
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
                raise ValueError('interval is mandatory')
        response = yield from self.client.put(path, data=json.dumps(data))
        return response.status == 200

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
