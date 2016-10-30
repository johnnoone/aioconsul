import logging
from aioconsul.common import (RequestHandler, Response, drop_null,
                              bool_to_int, timedelta_to_duration)
from aioconsul.encoders import json
from aioconsul.exceptions import (ConflictError,
                                  ConsulError,
                                  NotFound,
                                  UnauthorizedError)
from aioconsul.util import extract_attr
from collections import namedtuple
from functools import singledispatch
from copy import deepcopy

__all__ = ["API", "consul"]

logger = logging.getLogger(__name__)


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
        self.req_handler.json_loader = json.loads
        self._prepare_middlewares()

    def _prepare_middlewares(self):
        middlewares = [
            token_middleware,
            watch_middleware,
            consistency_middleware,
            body_middleware,
            parametrize_middleware,
        ]

        async def get_response(request):
            return await self.req_handler.request(**request)

        while middlewares:
            factory = middlewares.pop()
            get_response = factory(self, get_response)
        self.apply = get_response

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = extract_attr(token, keys=["ID"])

    @token.deleter
    def token(self):
        self._token = None

    @property
    def address(self):
        return self.req_handler.address

    async def get(self, *path, **kwargs):
        return await self.request("GET", *path, **kwargs)

    async def post(self, *path, **kwargs):
        return await self.request("POST", *path, **kwargs)

    async def put(self, *path, **kwargs):
        return await self.request("PUT", *path, **kwargs)

    async def delete(self, *path, **kwargs):
        return await self.request("DELETE", *path, **kwargs)

    async def request(self, method, *path, **kwargs):
        path = path_join(path)
        request = kwargs
        request.update({
            "path": path,
            "method": method,
            "headers": deepcopy(request.get("headers") or {}),
            "params": deepcopy(request.get("params") or {}),
        })
        response = await self.apply(request)
        return render(response)

    def close(self):
        if self.req_handler:
            self.req_handler.close()

    __del__ = close

    def __repr__(self):
        return "<%s(%r)>" % (self.__class__.__name__, self.address)


def path_join(path):
    if isinstance(path, (list, tuple)):
        path = ''.join(path_join(p) for p in path)
    path = '/%s' % path
    return path.replace('//', '/')


def extract_blocking(obj):
    """Extract index and watch from :class:`Blocking`

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


def format_duration(obj):
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    return timedelta_to_duration(obj)


def set_consistency(a, b, params):
    if a == "consistent":
        consistent, stale = True, None
    elif a == "stale":
        consistent, stale = None, True
    elif a == "default":
        consistent, stale = None, None

    elif params.get("consistent"):
        consistent, stale = True, None
    elif params.get("stale"):
        consistent, stale = None, True

    elif b == "consistent":
        consistent, stale = True, None
    elif b == "stale":
        consistent, stale = None, True
    elif b == "default":
        consistent, stale = None, None
    else:
        consistent, stale = None, None
    return consistent, stale


def consistency_middleware(ctx, get_response):
    """Set consistency

    Order:

    1. consistency request
    2. "stale" / "consistent" parameters
    3. ctx consistency
    """
    async def middleware(request):
        params = request.setdefault("params", {})
        consistency = request.pop("consistency", None)
        a, b = set_consistency(consistency, ctx.consistency, params)
        params["consistent"] = a
        params["stale"] = b
        return await get_response(request)
    return middleware


def token_middleware(ctx, get_response):
    """Reinject token and consistency into requests.
    """
    async def middleware(request):
        params = request.setdefault('params', {})
        if params.get("token") is None:
            params['token'] = ctx.token
        return await get_response(request)
    return middleware


def watch_middleware(ctx, get_response):
    async def middleware(request):
        watch = request.pop("watch", None)
        if watch:
            index, wait = extract_blocking(watch)
            params = request.setdefault("params", {})
            params.update({
                "index": index,
                "wait": format_duration(wait)
            })
        return await get_response(request)
    return middleware


def body_middleware(ctx, get_response):
    async def middleware(request):
        data = request.get("data", None)
        mime = request["headers"].get("Content-Type")
        if data is not None and not mime:
            data = drop_null(data)
            request["data"] = json.dumps(data)
            request["headers"]["Content-Type"] = "application/json"
        response = await get_response(request)
        return response
    return middleware


def parametrize_middleware(ctx, get_response):
    async def middleware(request):
        params = request.setdefault("params", {})
        if isinstance(params, dict):
            params = {k: bool_to_int(v) for k, v in params.items()}
        request["params"] = drop_null(params)
        return await get_response(request)
    return middleware


def render(response):
    logger.info("%r", response)
    if response.status >= 400:
        data = consul(response)
        if response.status in (401, 403):
            raise UnauthorizedError(data.value, meta=data.meta)
        if response.status == 404:
            raise NotFound(data.value, meta=data.meta)
        if response.status == 409:
            raise ConflictError(data.value, meta=data.meta)
        raise ConsulError(data.value, meta=data.meta)
    return response
