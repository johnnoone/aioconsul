import asyncio
from . import v1
from .bases import Token
from .request import RequestHandler, RequestWrapper


class Consul(RequestWrapper):
    """

    Most of the read query endpoints support multiple levels of consistency.
    Since no policy will suit all clients' needs, these consistency modes
    allow the user to have the ultimate say in how to balance the trade-offs
    inherent in a distributed system.
    """

    def __init__(self, api=None, *, token=None, consistency=None):
        api = str(api or 'http://127.0.0.1:8500').rstrip('/')
        if isinstance(token, Token):
            token = token.id
        handler = RequestHandler(api, 'v1',
                                 token=token,
                                 consistency=consistency)
        RequestWrapper.__init__(self, handler)

        self.acl = v1.ACLEndpoint(self.req_handler)
        self.agent = v1.AgentEndpoint(self.req_handler)
        self.catalog = v1.CatalogEndpoint(self.req_handler)
        self.event = v1.EventEndpoint(self.req_handler)
        self.health = v1.HealthEndpoint(self.req_handler)
        self.kv = v1.KVEndpoint(self.req_handler)
        self.session = v1.SessionEndpoint(self.req_handler)

    @property
    def api(self):
        return self.req_handler.api

    @property
    def version(self):
        return self.req_handler.version

    @property
    def token(self):
        return self.req_handler.token

    @property
    def consistency(self):
        return self.req_handler.consistency

    @asyncio.coroutine
    def request(self, method, path, **kwargs):
        response = yield from self.req_handler.request(method, path, **kwargs)
        return response
