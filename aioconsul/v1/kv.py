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

        Parameters:
            name (str): the datacenter name

        Returns:
            KVEndpoint: a clone of this endpoint, attached to dc

        """
        instance = copy.copy(self)
        instance.dc = name
        return instance

    @asyncio.coroutine
    def get(self, path):
        """Fetch one value

        Parameters:
            path (str): the key to check

        Returns:
            objects: The value corresponding to key.

        """
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
        """Fetch values by prefix

        Parameters:
            path (str): the prefix to check

        Returns:
            dict: Mapping of keys - objects
        """
        path = '/kv/%s' % path
        params = {'dc': self.dc,
                  'recurse': True}
        response = yield from self.client.get(path, params=params)
        data = yield from response.json()
        return {item['Key']: codec.decode(item) for item in data}

    @asyncio.coroutine
    def keys(self, path, *, separator=None):
        """Lists keys by prefix until separator

        Parameters:
            path (str): the prefix to check
            separator (str): fetch all keys until this separator

        Returns:
            set: a set of keys
        """
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
        """Deletes keys by path.
        If recurse is True, it will delete every keys prefixed by path.

        Parameters:
            path (str): the path to delete
            recurse (bool): delete recursively
            cas (str): CAS to check before delete

        Returns:
            bool: True
        """
        path = '/kv/%s' % path
        params = {'cas': cas,
                  'dc': self.dc,
                  'recurse': recurse}
        response = yield from self.client.delete(path, params=params)
        return response.status == 200
