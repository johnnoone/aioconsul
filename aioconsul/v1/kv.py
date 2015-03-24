import asyncio
import copy
import logging
from aioconsul.bases import Key
from aioconsul.response import render
from aioconsul.util import extract_id
from aioconsul.exceptions import HTTPError

logger = logging.getLogger(__name__)


class KVEndpoint:
    """
    Attributes:
        dc (str): the datacenter
    """

    class NotFound(ValueError):
        """Raised when a key was not found."""
        pass

    def __init__(self, client, dc=None):
        self.client = client
        self.dc = dc

    def dc(self, name):
        """
        Wraps requests to the specified datacenter.

        Parameters:
            name (str): datacenter name
        Returns:
            KVEndpoint: instance
        """
        instance = copy.copy(self)
        instance.dc = name
        return instance

    @asyncio.coroutine
    def keys(self, path, *, separator=None):
        """Returns all keys that starts with path

        Parameters:
            path (str): the key to fetch
            separator (str): everything until
        Returns:
            DataSet: a set of :class:`Key`
        """
        fullpath = 'kv/%s' % path
        params = {
            'dc': self.dc,
            'keys': True,
            'separator': separator
        }
        response = yield from self.client.get(fullpath, params=params)
        values = yield from response.json()
        return render(values, response=response)

    @asyncio.coroutine
    def acquire(self, path, *, session):
        """Acquire a key

        Parameters:
            path (str): the key
            session (Session): session or id

        Returns:
            bool: key has been acquired
        """
        fullpath = 'kv/%s' % path
        params = {
            'dc': self.dc,
            'acquire': extract_id(session)
        }
        response = yield from self.client.put(fullpath,
                                              params=params)
        return (yield from response.json())

    @asyncio.coroutine
    def release(self, path, *, session):
        """Release a key

        Parameters:
            path (str): the key
            session (Session): session or id
        Returns:
            bool: key has been released
        """
        fullpath = 'kv/%s' % path
        params = {
            'dc': self.dc,
            'release': extract_id(session)
        }
        response = yield from self.client.put(fullpath,
                                              params=params)
        return (yield from response.json())

    @asyncio.coroutine
    def set(self, path, obj, *, cas=None):
        """Sets a key - obj

        If CAS is providen, then it will acts as a Check and Set.
        CAS must be the ModifyIndex of that key

        Parameters:
            path (str): the key
            obj (object): any object type (will be compressed by codec)
            cas (str): modify_index of key
        Returns:
            bool: value has been setted
        """
        value, flags = encode(obj)
        return (yield from self.put(path, value, flags=flags, cas=cas))

    @asyncio.coroutine
    def put(self, path, value, *, flags=None, cas=None):
        """Sets a key - value (lowlevel)

        If the cas parameter is set, Consul will only put the key if it does
        not already exist. If the index is non-zero, the key is only set if
        the index matches the ModifyIndex of that key.

        Parameters:
            path (str): the key
            value (str): value to put
            flags (int): flags
            cas (int): modify_index of key
            acquire (str): session id
            release (str): session id
        Returns:
            bool: succeed
        """
        fullpath = 'kv/%s' % path
        params = {
            'dc': self.dc,
            'flags': flags,
            'cas': cas
        }
        response = yield from self.client.put(fullpath,
                                              params=params,
                                              data=value)
        return (yield from response.json())

    def delete(self, path, *, recurse=None, cas=None):
        """Deletes one or many keys.

        Parameters:
            path (str): the key to delete
            recurse (bool): delete all keys which have the specified prefix
            cas (str): turn the delete into a Check-And-Set operation.
        Returns:
            bool: succeed
        """
        fullpath = 'kv/%s' % path
        params = {
            'dc': self.dc,
            'recurse': recurse,
            'cas': cas
        }
        response = yield from self.client.delete(fullpath,
                                                 params=params)
        return response.status == 200

    @asyncio.coroutine
    def get(self, path):
        """Fetch one value

        The returned object has a special attribute named
        `consul` which holds the :class:`Key` informations.

        Parameters:
            path (str): exact match
        Returns:
            object: The value corresponding to key.
        Raises:
            NotFound: key was not found
        """
        fullpath = '/kv/%s' % path
        params = {'dc': self.dc}
        try:
            response = yield from self.client.get(fullpath, params=params)
            for item in (yield from response.json()):
                return decode(item)
        except HTTPError as error:
            if error.status == 404:
                raise self.NotFound('Key %r was not found' % path)

    @asyncio.coroutine
    def items(self, path):
        """Fetch values by prefix

        The returned objects has a special attribute named
        `consul` which holds the :class:`Key` informations.

        Parameters:
            path (str): prefix to check

        Returns:
            DataMapping: mapping of key names - values
        """
        path = '/kv/%s' % path
        params = {'dc': self.dc,
                  'recurse': True}
        response = yield from self.client.get(path, params=params)
        data = yield from response.json()
        logger.info('%s %s', data, response.headers)
        values = {item['Key']: decode(item) for item in data}

        return render(values, response=response)

    __call__ = items


class ConsulString(str):

    def __new__(cls, *args, consul, **kwargs):
        return str.__new__(cls, *args, **kwargs)

    def __init__(self, *args, consul, **kwargs):
        self.consul = consul


def encode(obj):
    # TODO implements flags encoding
    return str(obj), 0


def decode(data, base64=True):
    # TODO implements flags decoding
    from base64 import b64decode

    key = Key(name=data.get('Key'),
              create_index=data.get('CreateIndex'),
              lock_index=data.get('LockIndex'),
              modify_index=data.get('ModifyIndex'),
              session=data.get('Session'))
    value = data['Value']
    if base64:
        value = b64decode(value).decode('utf-8')
    return ConsulString(value, consul=key)
