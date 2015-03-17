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

    def __call__(self, **kwargs):
        cloned = copy.copy(self)
        if 'dc' in kwargs:
            cloned.dc = kwargs.pop('dc')
        if kwargs:
            logger.warn('some attrs where not used! %s', kwargs)
        return cloned

    @asyncio.coroutine
    def get(self, path):
        """fetch one key"""
        fullpath = '/kv/%s' % str(path).lstrip('/')
        params = {'dc': self.dc}
        try:
            response = yield from self.client.get(fullpath, params=params)
            for item in (yield from response.json()):
                return codec.decode(item)
        except HTTPError as error:
            if error.status == 404:
                raise self.NotFound('Key %r was not found' % path)

    @asyncio.coroutine
    def items(self, path, *, separator=None):
        """fetch keys by prefix until separator"""
        path = '/kv/%s' % str(path).lstrip('/')
        params = {'dc': self.dc,
                  'separator': separator,
                  'recurse': True}
        response = yield from self.client.get(path, params=params)
        return [codec.decode(item) for item in (yield from response.json())]

    @asyncio.coroutine
    def keys(self, path, *, separator=None):
        """list keys by prefix until separator"""
        path = '/kv/%s' % str(path).lstrip('/')
        params = {'dc': self.dc,
                  'keys': True,
                  'recurse': True,
                  'separator': separator}
        response = yield from self.client.get(path, params=params)
        return set((yield from response.json()))

    @asyncio.coroutine
    def set(self, path, value, *, flags=0, cas=None,
            acquire=None, release=None):
        path = '/kv/%s' % str(path).lstrip('/')
        params = {'dc': self.dc,
                  'flags': flags}
        if cas is not None:
            params['cas'] = cas
        if acquire is not None:
            params['acquire'] = acquire
        if acquire is not None:
            params['acquire'] = acquire
        response = yield from self.client.put(path, params=params, data=value)
        return (yield from response.text()).strip() == 'true'

    @asyncio.coroutine
    def delete(self, path, *, recurse=False, cas=None):
        path = '/kv/%s' % str(path).lstrip('/')
        params = {'cas': cas,
                  'dc': self.dc,
                  'recurse': recurse}
        response = yield from self.client.delete(path, params=params)
        return (yield from response.text())
