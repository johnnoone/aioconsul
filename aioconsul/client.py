import aiohttp
import asyncio
import logging
from . import endpoints
from .exceptions import HTTPError, UnknownLeader

log = logging.getLogger(__name__)


class Consul(object):

    def __init__(self, api=None, version=None):
        self.api = str(api or 'http://127.0.0.1:8500').rstrip('/')
        self.version = str(version or 'v1').strip('/')
        self.agent = endpoints.AgentEndpoint(self)
        self.catalog = endpoints.CatalogEndpoint(self)
        self.kv = endpoints.KVEndpoint(self)
        self.sessions = endpoints.SessionEndpoint(self)

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
        params = kwargs.setdefault('params', {})
        if params.get('dc', -1) is None:
            del params['dc']
        if params.get('cas', -1) is None:
            del params['cas']
        response = yield from aiohttp.request(method, url, **kwargs)
        if response.status == 200:
            return response

        headers = response.headers
        body = yield from response.text()
        if headers.get('X-Consul-KnownLeader', None) == 'false':
            raise UnknownLeader(body)

        log.error('%s %s %s %s %s', response.status, method, url, body, kwargs)
        raise HTTPError(response.status, body, url, data=kwargs)
