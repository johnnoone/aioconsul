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
        :returns: a clone of this endpoint, attached to dc
        :rtype: KVEndpoint
        """
        instance = copy.copy(self)
        instance.dc = name
        return instance

    @asyncio.coroutine
    def get(self, path):
        """Fetch one value

        :param path: the key to check
        :type path: str
        :returns: The value corresponding to key.
        :rtype: obj
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

        :param path: the prefix to check
        :type path: str
        :returns: a mapping of keys-values
        :rtype: dict
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

        :param path: the prefix to check
        :type path: str
        :param separator: fetch all keys until this separator
        :type separator: str
        :returns: a set of keys
        :rtype: set
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

        :param path: the path to delete
        :type path: str
        :param recurse: delete recursively
        :type recurse: bool
        :param cas: CAS to check before delete
        :type cas: str
        :returns: True
        """
        path = '/kv/%s' % path
        params = {'cas': cas,
                  'dc': self.dc,
                  'recurse': recurse}
        response = yield from self.client.delete(path, params=params)
        return response.status == 200
