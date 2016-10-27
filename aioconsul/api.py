import json
import logging
from aioconsul.common import RequestHandler, Response
from aioconsul.exceptions import (ConflictError,
                                  ConsulError,
                                  NotFound,
                                  UnauthorizedError)
from aioconsul.util import extract_attr
from collections import namedtuple
from collections.abc import Mapping
from functools import singledispatch

__all__ = ["API", "consul"]

logger = logging.getLogger(__name__)


def render(response):
    logger.info("%r", response)
    if response.status >= 400:
        data = consul(response)
        if response.status in (401, 403):
            raise UnauthorizedError(data.value, meta=data.meta)
        if response.status == 404:
            raise NotFound(data.value, meta=data.meta)
        if response.status == 409:
            value = data.value
            if isinstance(value, Mapping):
                value = value.get("Errors", value)
            raise ConflictError(value, meta=data.meta)
        raise ConsulError(data.value, meta=data.meta)
    return response


class API:

    """

    Attributes:
        token (str): Token ID
        consistency (Consistency): One of the value as defined by
                                   :class:`~aioconsul.typing.Consistency`
    """

    def __init__(self, address, *, token=None, consistency=None, loop=None):
        self.token = token
        self.consistency = consistency
        self.req_handler = RequestHandler(address, loop=loop)
        self.req_handler.on_prepare.connect(self._prepare_request)

    @property
    def address(self):
        return self.req_handler.address

    def _prepare_request(self, sender, method, path, **kwargs):
        """Reinject token and consistency into requests.
        """
        params = kwargs.setdefault('params', {})
        params.setdefault('token', self.token)
        if self.consistency == 'consistent' and 'stale' not in params:
            params.setdefault('consistent', True)
        if self.consistency == 'stale' and 'consistent' not in params:
            params.setdefault('stale', True)
        return kwargs

    async def get(self, *path, **kwargs):
        return await self.request("GET", *path, **kwargs)

    async def post(self, *path, **kwargs):
        return await self.request("POST", *path, **kwargs)

    async def put(self, *path, **kwargs):
        return await self.request("PUT", *path, **kwargs)

    async def delete(self, *path, **kwargs):
        return await self.request("DELETE", *path, **kwargs)

    async def request(self, method, *path, **kwargs):
        # TODO maybe not the right place, but...
        path = flatten_path(path)
        params = kwargs.setdefault("params", {})
        watch = kwargs.pop("watch", None)
        if watch:
            index, wait = extract_blocking(watch)
            params.update({
                "index": index,
                "wait": wait
            })
        consistency = kwargs.pop("consistency", None)
        if consistency is not None:
            params.pop("stale", None)
            params.pop("consistent", None)
            params["consistent" if consistency else "stale"] = True

        response = await self.req_handler.request(method, path, **kwargs)
        return render(response)

    def __repr__(self):
        return "<%s(%r)>" % (self.__class__.__name__, self.address)


def flatten_path(path):
    if isinstance(path, (list, tuple)):
        path = ''.join(flatten_path(p) for p in path)
    path = '/%s' % path
    return path.replace('//', '/')


def extract_blocking(obj):
    """Extract index and watch from :class:`Blocking`.

    Parameters:
        obj (Blocking): the blocking object
    Returns:
        tuple: index and watch
    """
    if isinstance(obj, tuple):
        try:
            a, b = obj
        except:
            raise TypeError("Not a Blocking object")
    else:
        a, b = obj, None
    return extract_attr(a, keys=["Index"]), b


ConsulValue = namedtuple('ConsulValue', 'value meta')


@singledispatch
def consul(obj, meta=None):
    meta = meta or {}
    return ConsulValue(obj, meta=meta)


@consul.register(Response)
def consul_response(obj, meta=None):
    meta = meta or {}
    for k, v in extract_meta(obj.headers).items():
        meta.setdefault(k, v)
    return ConsulValue(obj.body, meta=meta)


def extract_meta(headers):
    meta = {}
    for k, v in headers.items():
        if k.lower().startswith("x-consul-"):
            k = k[9:]
            k = {
                'index': 'Index',
                'knownleader': 'KnownLeader',
                'lastcontact': 'LastContact',
                'token': 'Token',
                'translate-addresses': 'Translate-Addresses',
            }.get(k.lower(), k)
            meta[k] = json.loads(v)
    return meta
