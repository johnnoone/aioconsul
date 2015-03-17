import asyncio
import logging
from .check import AgentCheckEndpoint
from .service import AgentServiceEndpoint

log = logging.getLogger(__name__)


class AgentEndpoint:

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
        response = yield from self.client.put('/agent/maintenance',
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
    params['address'] = data.pop('Addr', None)
    params['name'] = data.pop('Name', None)
    params['port'] = data.pop('Port', None)
    params['status'] = data.pop('Status', None)
    params['tags'] = data.pop('Tags', None)
    params['delegate_cur'] = data.pop('DelegateCur', None)
    params['delegate_max'] = data.pop('DelegateMax', None)
    params['delegate_min'] = data.pop('DelegateMin', None)
    params['protocol_cur'] = data.pop('ProtocolCur', None)
    params['protocol_max'] = data.pop('ProtocolMax', None)
    params['protocol_min'] = data.pop('ProtocolMin', None)
    if data:
        logger.warn('Not used %s', data)
    return Member(**params)
