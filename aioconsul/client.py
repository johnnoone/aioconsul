import aiohttp
import asyncio
import logging
from . import v1
from .exceptions import HTTPError, UnknownLeader

log = logging.getLogger(__name__)


class Consul:

    def __init__(self, api=None):
        self.api = str(api or 'http://127.0.0.1:8500').rstrip('/')
        self.version = 'v1'
        self.acl = v1.ACLEndpoint(self)
        self.agent = v1.AgentEndpoint(self)
        self.catalog = v1.CatalogEndpoint(self)
        self.event = v1.EventEndpoint(self)
        self.health = v1.HealthEndpoint(self)
        self.kv = v1.KVEndpoint(self)
        self.session = v1.SessionEndpoint(self)

    @asyncio.coroutine
    def get(self, path, **kwargs):
        response = yield from self.request('GET', path, **kwargs)
        return response

    @asyncio.coroutine
    def post(self, path, **kwargs):
        response = yield from self.request('POST', path, **kwargs)
        return response

    @asyncio.coroutine
    def put(self, path, **kwargs):
        response = yield from self.request('PUT', path, **kwargs)
        return response

    @asyncio.coroutine
    def delete(self, path, **kwargs):
        response = yield from self.request('DELETE', path, **kwargs)
        return response

    @asyncio.coroutine
    def request(self, method, path, **kwargs):
        url = '%s/%s/%s' % (self.api, self.version, path.lstrip('/'))

        def parameters(data):

            def prepare(value):
                if value is True:
                    return 'true'
                if value is False:
                    return 'false'
                return value

            return {k: prepare(v) for k, v in data.items() if v is not None}

        kwargs['params'] = parameters(kwargs.setdefault('params', {}))
        response = yield from aiohttp.request(method, url, **kwargs)
        if response.status == 200:
            return response

        headers = response.headers
        body = yield from response.text()
        if headers.get('X-Consul-KnownLeader', None) == 'false':
            raise UnknownLeader(body)

        log.warn('%s %s %s %s %s', response.status, method, url, body, kwargs)
        raise HTTPError(response.status, body, url, data=kwargs)
