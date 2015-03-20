import asyncio
import copy
import json
import logging
from aioconsul.bases import Session
from aioconsul.util import extract_id

log = logging.getLogger(__name__)


class SessionEndpoint:

    class NotFound(ValueError):
        pass

    def __init__(self, client, dc=None):
        self.client = client
        self.dc = dc

    def dc(self, name):
        """
        Wraps requests to the specified dc.

        Parameters:
            name (str): the datacenter name

        Returns:
            SessionEndpoint: a clone of this instance
        """
        instance = copy.copy(self)
        instance.dc = name
        return instance

    @asyncio.coroutine
    def create(self, *, name=None, node=None, checks=None,
               behavior=None, lock_delay=None, ttl=None):
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
        response = yield from self.client.put(path,
                                              params=params,
                                              data=json.dumps(data))
        if response.status == 200:
            return decode((yield from response.json()))

    @asyncio.coroutine
    def delete(self, session):
        path = '/session/destroy/%s' % extract_id(session)
        params = {'dc': self.dc}
        response = yield from self.client.put(path, params=params)
        return response.status == 200

    destroy = delete

    @asyncio.coroutine
    def get(self, session):
        path = '/session/info/%s' % extract_id(session)
        params = {'dc': self.dc}
        response = yield from self.client.get(path, params=params)
        items = yield from response.json()
        for item in (items or []):
            return decode(item)
        raise self.NotFound('Session %r was not found' % extract_id(session))

    @asyncio.coroutine
    def node(self, node):
        path = '/session/node/%s' % extract_id(node)
        params = {'dc': self.dc}
        response = yield from self.client.get(path, params=params)
        return [decode(item) for item in (yield from response.json())]

    @asyncio.coroutine
    def items(self):
        path = '/session/list'
        params = {'dc': self.dc}
        response = yield from self.client.get(path, params=params)
        return [decode(item) for item in (yield from response.json())]

    @asyncio.coroutine
    def renew(self, session):
        path = '/session/renew/%s' % extract_id(session)
        params = {'dc': self.dc}
        response = self.client.put(path, params=params)
        return response.status == 200


def decode(item):
    params = {}
    params['id'] = item.get('ID', None)
    params['behavior'] = item.get('Behavior', None)
    params['checks'] = item.get('Checks', None)
    params['create_index'] = item.get('CreateIndex', None)
    params['node'] = item.get('Node', None)
    return Session(**params)
