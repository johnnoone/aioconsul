import asyncio
import copy
import logging
from aioconsul import codec
from aioconsul.exceptions import HTTPError

logger = logging.getLogger(__name__)


class KVEndpoint:

    class NotFound(ValueError):
        pass

    def __init__(self, client, dc=None):
        self.client = client
        self.dc = dc

    def dc(self, name):
        """
        Wraps requests to the specified dc.

        :param name: the datacenter name
        """
        instance = copy.copy(self)
        instance.dc = name
        return instance

    @asyncio.coroutine
    def get(self, path):
        """Fetch one value"""
        fullpath = '/kv/%s' % path
        params = {'dc': self.dc}
        try:
            response = yield from self.client.get(fullpath, params=params)
            for item in (yield from response.json()):
                return codec.decode(item)
        except HTTPError as error:
            if error.status == 404:
                raise self.NotFound('Key %r was not found' % path)

    @asyncio.coroutine
    def items(self, path):
        """fetch values by prefix"""
        path = '/kv/%s' % path
        params = {'dc': self.dc,
                  'recurse': True}
        response = yield from self.client.get(path, params=params)
        data = yield from response.json()
        return {item['Key']: codec.decode(item) for item in data}

    @asyncio.coroutine
    def keys(self, path, *, separator=None):
        """list keys by prefix until separator"""
        path = '/kv/%s' % path
        params = {'dc': self.dc,
                  'keys': True,
                  'recurse': True,
                  'separator': separator}
        response = yield from self.client.get(path, params=params)
        return set((yield from response.json()))

    @asyncio.coroutine
    def set(self, path, value, *, flags=0, cas=None,
            acquire=None, release=None):
        path = '/kv/%s' % path
        params = {'dc': self.dc,
                  'flags': flags,
                  'cas': cas,
                  'acquire': acquire,
                  'release': release}
        response = yield from self.client.put(path, params=params, data=value)
        return (yield from response.text()).strip() == 'true'

    @asyncio.coroutine
    def delete(self, path, *, recurse=False, cas=None):
        path = '/kv/%s' % path
        params = {'cas': cas,
                  'dc': self.dc,
                  'recurse': recurse}
        response = yield from self.client.delete(path, params=params)
        return (yield from response.text())
