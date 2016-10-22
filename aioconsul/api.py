from aioconsul.common import RequestHandler
from aioconsul.exceptions import (ConflictError,
                                  ConsulError,
                                  NotFound,
                                  UnauthorizedError)
from aioconsul.common import decode_watch, Response  # noqa
from aioconsul.structures import consul
from collections.abc import Mapping
import logging

__all__ = ["API"]

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
        consistency (str): accept one of these values:
                           ``default``, ``consistent`` or ``stale``
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
            index, wait = decode_watch(watch)
            params.update({
                "index": index,
                "wait": wait
            })
        consistency = kwargs.pop("consistency", None)
        if consistency:
            params.pop("stale", None)
            params.pop("consistent", None)
            params[consistency] = True

        response = await self.req_handler.request(method, path, **kwargs)
        return render(response)

    def __repr__(self):
        return "<%s(%r)>" % (self.__class__.__name__, self.address)


def flatten_path(path):
    if isinstance(path, (list, tuple)):
        path = ''.join(flatten_path(p) for p in path)
    path = '/%s' % path
    return path.replace('//', '/')
