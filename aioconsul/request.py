import aiohttp
import asyncio
import logging
from .exceptions import ACLPermissionDenied, HTTPError, UnknownLeader


log = logging.getLogger(__name__)


class RequestHandler:

    def __init__(self, api, version=None, *, token=None, consistency=None):
        self.api = api
        self.version = version or 'v1'
        self.token = token
        self.consistency = consistency

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

        params = kwargs.get('params', {}).copy()
        params.setdefault('token', self.token)
        if self.consistency == 'consistent':
            params.setdefault('consistent', True)
        elif self.consistency == 'stale':
            params.setdefault('stale', True)
        kwargs['params'] = parameters(params)
        response = yield from aiohttp.request(method, url, **kwargs)

        if response.status == 200:
            log.info('%s %s %s %s', response.status, method, url, kwargs)
            return response

        headers = response.headers
        body = yield from response.text()

        log.warn('%s %s %s %s %s', response.status, method, url, body, kwargs)

        if headers.get('X-Consul-KnownLeader', None) == 'false':
            raise UnknownLeader(response.status, body, url, data=kwargs)

        if response.status == 403:
            raise ACLPermissionDenied(response.status, body, url, data=kwargs)

        raise HTTPError(response.status, body, url, data=kwargs)


class RequestWrapper:
    def __init__(self, req_handler):
        self.req_handler = req_handler

    @asyncio.coroutine
    def get(self, path, **kwargs):
        response = yield from self.request('get', path, **kwargs)
        return response

    @asyncio.coroutine
    def post(self, path, **kwargs):
        response = yield from self.request('post', path, **kwargs)
        return response

    @asyncio.coroutine
    def put(self, path, **kwargs):
        response = yield from self.request('put', path, **kwargs)
        return response

    @asyncio.coroutine
    def delete(self, path, **kwargs):
        response = yield from self.request('delete', path, **kwargs)
        return response

    @asyncio.coroutine
    def request(self, method, path, **kwargs):
        raise NotImplementedError()
