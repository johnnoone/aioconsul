import aiohttp
import asyncio
from .addr import parse_addr
from .objs import Response
from .util import drop_null, json_decode, json_encode, bool_to_int
from blinker import Signal


class RequestHandler:

    on_prepare = Signal()

    def __init__(self, address, *, loop=None):
        self.address = parse_addr(address, proto="http", host="localhost")
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def request(self, method, path, **kwargs):
        data = self.on_prepare.send(self, method=method, path=path, **kwargs)
        for func, overwrites in data:
            if overwrites is not None:
                # do not allow to overwrite method and path
                overwrites.pop('method', None)
                overwrites.pop('path', None)
                kwargs.update(overwrites)

        url = "%s/%s" % (self.address.__str__(), path.lstrip("/"))
        kwargs = json_middleware(**kwargs)
        kwargs["params"] = parametrize(kwargs.get("params", None))
        async with self.session.request(method, url, **kwargs) as response:
            return await render(response, url=url, method=method)

    __call__ = request

    def close(self):
        self.session.close()

    __del__ = close


def json_middleware(**kwargs):
    if "json" in kwargs:
        data = drop_null(kwargs.pop("json"))
        kwargs["data"] = json_encode(data)
        headers = kwargs.setdefault("headers", {})
        headers.setdefault("Content-Type", "application/json")
    return kwargs


def parametrize(params):
    params = drop_null(params)
    if isinstance(params, dict):
        return {k: bool_to_int(v) for k, v in params.items()}
    return params


async def render(response, url=None, method=None):
    # response.raise_for_status()
    if response.headers.get("Content-Type") == "application/json":
        body = await response.json(encoding="utf-8", loads=json_decode)
    else:
        body = await response.read()
    return Response(url=url,
                    status=response.status,
                    body=body,
                    headers=response.headers,
                    method=method)
