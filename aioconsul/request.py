import aiohttp
import logging
from .util import task, mark_task


log = logging.getLogger(__name__)


class RequestHandler:
    """
    Attributes:
        host (str): host api
        version (str): api version
        token (str): Token ID
        consistency (str): default, consistent or stale
    """

    def __init__(self, host, version, *, token=None, consistency=None):
        self.host = host
        self.version = version
        self.token = token
        self.consistency = consistency

    def get(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('GET', path, **kwargs)

    def post(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('POST', path, **kwargs)

    def put(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('PUT', path, **kwargs)

    def delete(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('DELETE', path, **kwargs)

    @task
    def request(self, method, path, **kwargs):
        url = '%s/%s/%s' % (self.host, self.version, path.lstrip('/'))

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
        if self.consistency == 'consistent' and 'stale' not in params:
            params.setdefault('consistent', True)
        if self.consistency == 'stale' and 'consistent' not in params:
            params.setdefault('stale', True)
        kwargs['params'] = parameters(params)
        response = yield from aiohttp.request(method, url, **kwargs)

        if response.status == 200:
            log.info('%s %s %s %s', response.status, method, url, kwargs)
        else:
            log.warn('%s %s %s %s', response.status, method, url, kwargs)
        return response


class RequestWrapper:
    def __init__(self, req_handler):
        self.req_handler = req_handler

    @mark_task
    def get(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('get', path, **kwargs)

    @mark_task
    def post(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('post', path, **kwargs)

    @mark_task
    def put(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('put', path, **kwargs)

    @mark_task
    def delete(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('delete', path, **kwargs)

    @mark_task
    def request(self, method, path, **kwargs):
        raise NotImplementedError()
