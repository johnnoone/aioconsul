import asyncio
import copy
import json
import logging
from aioconsul.util import extract_id

log = logging.getLogger(__name__)


class SessionEndpoint(object):

    def __init__(self, client, dc=None):
        self.client = client
        self.dc = dc

    def __call__(self, **kwargs):
        cloned = copy.copy(self)
        if 'dc' in kwargs:
            cloned.dc = kwargs.pop('dc')
        if kwargs:
            log.warn('some attrs where not used! %s', kwargs)
        return cloned

    @asyncio.coroutine
    def create(self, *, lock_delay=None, node=None, name=None, checks=None, behavior=None, ttl=None):
        path = '/session/create'
        params = {'dc': self.dc}
        data = {}
        if lock_delay:
            data['LockDelay'] = lock_delay
        if node:
            data['Node'] = node
        if name:
            data['Name'] = name
        if checks:
            data['Checks'] = checks
        if behavior:
            data['Behavior'] = behavior
        if ttl is not None:
            data['TTL'] = ttl
        response = self.client.put(path, params=params, data=json.dumps(data))
        if response.status == 200:
            return (yield from response.json())['ID']

    @asyncio.coroutine
    def destroy(self, session):
        path = '/session/destroy/%s' % extract_id(session)
        params = {'dc': self.dc}
        response = self.client.put(path, params=params)
        return response.status == 200

    @asyncio.coroutine
    def info(self, session):
        path = '/session/info/%s' % extract_id(session)
        params = {'dc': self.dc}
        response = self.client.get(path, params=params)
        return (yield from response.json())

    @asyncio.coroutine
    def node(self, node):
        path = '/session/node/%s' % extract_id(node)
        params = {'dc': self.dc}
        response = self.client.get(path, params=params)
        return (yield from response.json())

    @asyncio.coroutine
    def items(self):
        path = '/session/list'
        params = {'dc': self.dc}
        response = self.client.get(path, params=params)
        return (yield from response.json())

    @asyncio.coroutine
    def renew(self, session):
        path = '/session/renew/%s' % extract_id(session)
        params = {'dc': self.dc}
        response = self.client.put(path, params=params)
        return response.status == 200
