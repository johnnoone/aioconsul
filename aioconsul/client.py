import asyncio
from . import v1
from .bases import Token
from .request import RequestHandler, RequestWrapper
from .util import lazy_property, mark_task


class Consul(RequestWrapper):
    """

    Most of the read query endpoints support multiple levels of consistency.
    Since no policy will suit all clients' needs, these consistency modes
    allow the user to have the ultimate say in how to balance the trade-offs
    inherent in a distributed system.

    Attributes:
        host (str): host api
        version (str): api version
        token (str): Token ID
        consistency (str): default, consistent or stale
    """

    def __init__(self, host=None, *, token=None, consistency=None, loop=None):
        host = str(host or 'http://127.0.0.1:8500').rstrip('/')
        if isinstance(token, Token):
            token = token.id
        handler = RequestHandler(host, 'v1', token=token,
                                 consistency=consistency)
        RequestWrapper.__init__(self, handler)

        self.loop = loop or asyncio.get_event_loop()

    @lazy_property
    def acl(self):
        """Implements :ref:`acl endpoint <acl>`."""
        return v1.ACLEndpoint(self.req_handler, loop=self.loop)

    @lazy_property
    def agent(self):
        """Implements :ref:`agent endpoint <agent>`."""
        return v1.AgentEndpoint(self.req_handler, loop=self.loop)

    @lazy_property
    def catalog(self):
        """Implements :ref:`catalog endpoint <catalog>`."""
        return v1.CatalogEndpoint(self.req_handler, loop=self.loop)

    @lazy_property
    def events(self):
        """Implements :ref:`event endpoint <event>`."""
        return v1.EventEndpoint(self.req_handler, loop=self.loop)

    @lazy_property
    def health(self):
        """Implements :ref:`health endpoint <health>`."""
        return v1.HealthEndpoint(self.req_handler, loop=self.loop)

    @lazy_property
    def kv(self):
        """Implements :ref:`kv endpoint <kv>`."""
        return v1.KVEndpoint(self.req_handler, loop=self.loop)

    @lazy_property
    def sessions(self):
        """Implements :ref:`session endpoint <session>`."""
        return v1.SessionEndpoint(self.req_handler, loop=self.loop)

    @property
    def host(self):
        return self.req_handler.host

    @property
    def version(self):
        return self.req_handler.version

    @property
    def token(self):
        return self.req_handler.token

    @property
    def consistency(self):
        return self.req_handler.consistency

    @mark_task
    def request(self, method, path, **kwargs):
        """
        Makes single http request.

        Requested url will be in the form of ``{host}/{version}/{path}``

        Parameters:
            method (str): http method
            path (str): path after version
        Keyword Arguments:
            params (dict): get params
            data (str): body of the request
            headers (dict): custom headers
        Returns:
            asyncio.Task: the request
        """
        return self.req_handler.request(method, path, **kwargs)
