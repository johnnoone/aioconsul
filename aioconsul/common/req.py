import aiohttp
import asyncio
import json
from .addr import parse_addr
from .objs import Response


class RequestHandler:

    def __init__(self, address, *, loop=None):
        self.address = parse_addr(address, proto="http", host="localhost")
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.json_loader = json.loads

    async def request(self, method, path, **kwargs):
        url = "%s/%s" % (self.address.__str__(), path.lstrip("/"))
        async with self.session.request(method, url, **kwargs) as response:
            if response.headers.get("Content-Type") == "application/json":
                body = await response.json(encoding="utf-8",
                                           loads=self.json_loader)
            else:
                body = await response.read()
            return Response(path=path,
                            status=response.status,
                            body=body,
                            headers=response.headers,
                            method=method)

    __call__ = request

    def close(self):
        self.session.close()

    __del__ = close
