import asyncio
import logging
from .nodes import CatalogNodeEndpoint
from .services import CatalogServiceEndpoint

log = logging.getLogger(__name__)


class CatalogEndpoint:

    def __init__(self, client):
        self.client = client
        self.nodes = CatalogNodeEndpoint(client)
        self.services = CatalogServiceEndpoint(client)

    @asyncio.coroutine
    def register(self, node, address, *, dc=None, check=None, service=None):
        raise NotImplementedError()

    @asyncio.coroutine
    def deregister(self):
        raise NotImplementedError()

    @asyncio.coroutine
    def datacenters(self):
        response = yield from self.client.get('/catalog/datacenters')
        return (yield from response.json())
