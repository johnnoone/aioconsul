import asyncio
import copy
import logging
from aioconsul.bases import Key
from aioconsul.response import render, render_meta
from aioconsul.util import extract_id, extract_ref, task
from aioconsul.exceptions import PermissionDenied, ValidationError, HTTPError
from aioconsul.types import ConsulString

logger = logging.getLogger(__name__)


class KVEndpoint:
    """
    Attributes:
        dc (str): the datacenter
    """

    class NotFound(ValueError):
        """Raised when a key was not found."""
        pass

    def __init__(self, client, *, loop=None, dc=None):
        self.client = client
        self.dc = dc
        self.loop = loop or asyncio.get_event_loop()

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

    @task
    def keys(self, prefix, *, separator=None):
        """Returns all keys that starts with path

        Parameters:
            prefix (str): the prefix to fetch
            separator (str): everything until
        Returns:
            ConsulSet: a set of :class:`Key`
        """
        path = 'kv/%s' % prefix
        params = {
            'dc': self.dc,
            'keys': True,
            'separator': separator
        }

        response = yield from self.client.get(path, params=params)
        if response.status == 200:
            values = yield from response.json()
            return render(values, response=response)
        yield from fail(response)

    @task
    def acquire(self, key, *, session):
        """Acquire a key

        Parameters:
            path (str): the key
            session (Session): session or id
        Returns:
            bool: key has been acquired
        """
        path = 'kv/%s' % key
        params = {
            'dc': self.dc,
            'acquire': extract_id(session)
        }
        response = yield from self.client.put(path, params=params)
        if response.status == 200:
            return (yield from response.json())
        yield from fail(response)

    @task
    def release(self, key, *, session):
        """Release a key

        Parameters:
            path (str): the key
            session (Session): session or id
        Returns:
            bool: key has been released
        """
        path = 'kv/%s' % key
        params = {
            'dc': self.dc,
            'release': extract_id(session)
        }
        response = yield from self.client.put(path, params=params)
        if response.status == 200:
            return (yield from response.json())
        yield from fail(response)

    def set(self, key, obj, *, cas=None):
        """Sets a key - obj

        If CAS is providen, then it will acts as a Check and Set.
        CAS must be the ModifyIndex of that key

        Parameters:
            path (str): the key
            obj (object): any object type (will be compressed by codec)
            cas (int): modify_index of key
        Returns:
            bool: value has been setted
        """
        value, flags = encode(obj)
        return self.put(key, value, flags=flags, cas=cas)

    @task
    def put(self, key, value, *, flags=None, cas=None):
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
        path = 'kv/%s' % key
        if cas:
            cas = extract_ref(cas)

        params = {
            'dc': self.dc,
            'flags': flags,
            'cas': cas
        }

        response = yield from self.client.put(path,
                                              params=params,
                                              data=value)
        if response.status == 200:
            return (yield from response.json())
        yield from fail(response)

    @task
    def delete(self, path, *, recurse=None, cas=None):
        """Deletes one or many keys.

        Parameters:
            path (str): the key to delete
            recurse (bool): delete all keys which have the specified prefix
            cas (int): turn the delete into a Check-And-Set operation.
        Returns:
            bool: succeed
        """
        path = 'kv/%s' % path
        if cas:
            cas = extract_ref(cas)
        params = {
            'dc': self.dc,
            'recurse': recurse,
            'cas': cas
        }

        response = yield from self.client.delete(path, params=params)
        if response.status == 200:
            return (yield from response.json())
        yield from fail(response)

    @task
    def meta(self, key=None, *, prefix=None):
        """Returns the meta of a key, or a prefix

        Parameters:
            key (str): look this key
            prefix (str): look this prefix
        Returns:
            ConsulMeta: meta of this path
        """

        if key and prefix:
            raise ValidationError('key and prefix are mutually exclusive')

        elif key:
            path = '/kv/%s' % key
            recursive = None
        elif prefix:
            path = '/kv/%s' % prefix
            recursive = True
        else:
            raise ValidationError('key or prefix required')

        params = {'dc': self.dc,
                  'recursive': recursive}

        response = yield from self.client.get(path, params=params)
        return render_meta(response)

    @task
    def get(self, key, *, watch=None):
        """Fetch one value

        The returned object has a special attribute named
        `consul` which holds the :class:`Key` informations.

        Parameters:
            path (str): exact match
            watch (int): wait for changes
        Returns:
            object: value corresponding to key.
        Raises:
            NotFound: key was not found
        """

        path = '/kv/%s' % key
        params = {'dc': self.dc}
        index = None
        if watch not in (None, True, False):
            index = extract_ref(watch)
            params.update({
                'index': extract_ref(watch),
                'wait': '10m'
            })

        while True:
            response = yield from self.client.get(path, params=params)
            meta = render_meta(response)
            if index == meta.last_index:
                continue
            elif response.status == 200:
                for item in (yield from response.json()):
                    return decode(item)
            elif response.status == 404:
                err = self.NotFound('Key %r was not found' % path)
                err.consul = render_meta(response)
                raise err
            yield from fail(response)

    @task
    def items(self, path, watch=None):
        """Fetch values by prefix

        The returned objects has a special attribute named
        `consul` which holds the :class:`Key` informations.

        Parameters:
            path (str): prefix to check
            watch (int): wait for changes
        Returns:
            ConsulMapping: mapping of key names - values
        """

        path = '/kv/%s' % path
        params = {'dc': self.dc,
                  'recurse': True}
        if watch not in (None, True, False):
            params.update({'index': extract_ref(watch),
                           'watch': '10m'})

        response = yield from self.client.get(path, params=params)
        if response.status == 200:
            data = yield from response.json()
            values = {item['Key']: decode(item) for item in data}
            return render(values, response=response)
        yield from fail(response)

    __call__ = items


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
    value = ConsulString(value)
    value.consul = key
    return value


@asyncio.coroutine
def fail(response):
    msg = yield from response.text()
    if response.status in (401, 403):
        err = PermissionDenied(msg)
    else:
        err = HTTPError(msg, response.status)
    err.consul = render_meta(response)
    raise err
