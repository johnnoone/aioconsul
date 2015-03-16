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
        return [decode_member(item) for item in (yield from response.json())]

    @asyncio.coroutine
    def me(self):
        response = yield from self.client.get('/agent/self')
        data = yield from response.json()
        if 'Member' in data:
            data['Member'] = decode_member(data['Member'])
        return data

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

    class NotFound(ValueError):
        pass

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def get(self, service):
        response = yield from self.client.get('/agent/services')
        items = yield from response.json()
        service_id = extract_id(service)
        try:
            return decode_service(items[service_id])
        except KeyError:
            raise self.NotFound('Service %r was not found' % service_id)

    @asyncio.coroutine
    def items(self):
        response = yield from self.client.get('/agent/services')
        items = yield from response.json()
        return [decode_service(item) for item in items.values()]

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


class Member:
    def __init__(self, name, address, port, **params):
        self.name = name
        self.address = name
        self.port = port
        for k, v in params.items():
            setattr(self, k, v)

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return '<Member(name=%r, address=%r, port=%r)>' % (
            self.name, self.address, self.port) 


def decode_member(data):
    params = {}
    params['address'] = data.get('Addr')
    params['name'] = data.get('Name')
    params['port'] = data.get('Port')
    params['status'] = data.get('Status')
    params['tags'] = data.get('Tags')
    params['delegate_cur'] = data.get('DelegateCur')
    params['delegate_max'] = data.get('DelegateMax')
    params['delegate_min'] = data.get('DelegateMin')
    params['protocol_cur'] = data.get('ProtocolCur')
    params['protocol_max'] = data.get('ProtocolMax')
    params['protocol_min'] = data.get('ProtocolMin')
    return Member(**params)


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


def decode_service(data):
    params = {}
    params['id'] = data.get('ID')
    params['name'] = data.get('Name')
    params['address'] = data.get('Address')
    params['port'] = data.get('Port')
    params['tags'] = data.get('Tags')
    return Service(**params)
