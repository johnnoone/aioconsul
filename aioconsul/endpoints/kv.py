import asyncio
import copy
import logging
from aioconsul import codec
from aioconsul.exceptions import HTTPError
from base64 import b64decode

log = logging.getLogger(__name__)


class KVEndpoint(object):

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
            log.warn('some attrs where not used! %s', kwargs)
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
                  'recurse': True}
        response = yield from self.client.get(path, params=params)
        return (yield from response.json())

    @asyncio.coroutine
    def set(self, path, value, *, flags=0, cas=None, acquire=None, release=None):
        """docstring for put"""
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
        """docstring for put"""
        path = '/kv/%s' % str(path).lstrip('/')
        params = {'cas': cas,
                  'dc': self.dc,
                  'recurse': recurse}
        response = yield from self.client.delete(path, params=params)
        return (yield from response.text())


class Item(object):
    def __init__(self, key, value, *, create_index=None, lock_index=None, modify_index=None):
        self.key = key
        self.value = value
        self.create_index = create_index
        self.lock_index = lock_index
        self.modify_index = modify_index

    def __repr__(self):
        return '<Item(key=%r, value=%r)>' % (self.key, self.value)


def load_item(data, Item=Item):
    """Loads item from API data."""
    params = {}
    if 'Key' in data:
        params['key'] = data['Key']
    if 'Value' in data:
        value = b64decode(data['Value']).decode('utf-8')
        if data.get('Flags', None):
            log.warn('not implemented yet')
        params['value'] = value
    params['create_index'] = data.get('CreateIndex', None)
    params['lock_index'] = data.get('LockIndex', None)
    params['modify_index'] = data.get('ModifyIndex', None)
    return Item(**params)
