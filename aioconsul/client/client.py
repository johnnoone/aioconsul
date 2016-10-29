from aioconsul.api import API
from aioconsul.common import cached_property
from .acl_endpoint import ACLEndpoint
from .agent_endpoint import AgentEndpoint
from .catalog_endpoint import CatalogEndpoint
from .checks_endpoint import ChecksEndpoint
from .coordinate_endpoint import CoordinateEndpoint
from .event_endpoint import EventEndpoint
from .health_endpoint import HealthEndpoint
from .kv_endpoint import KVEndpoint
from .members_endpoint import MembersEndpoint
from .operator_endpoint import OperatorEndpoint
from .query_endpoint import QueryEndpoint
from .services_endpoint import ServicesEndpoint
from .session_endpoint import SessionEndpoint
from .status_endpoint import StatusEndpoint

__all__ = ["Consul"]


class Consul:

    def __init__(self, address, *, token=None, consistency=None, loop=None):
        self.api = API(address,
                       token=token,
                       consistency=consistency,
                       loop=loop)

    @property
    def address(self):
        return self.api.address

    @property
    def token(self):
        return self.api.token

    @token.setter
    def token(self, token):
        self.api.token = token

    @token.deleter
    def token(self):
        del self.api.token

    @property
    def consistency(self):
        return self.api.consistency

    @cached_property
    def acl(self):
        return ACLEndpoint(self.api)

    @cached_property
    def agent(self):
        return AgentEndpoint(self.api)

    @cached_property
    def catalog(self):
        return CatalogEndpoint(self.api)

    @cached_property
    def checks(self):
        return ChecksEndpoint(self.api)

    @cached_property
    def coordinate(self):
        return CoordinateEndpoint(self.api)

    @cached_property
    def event(self):
        return EventEndpoint(self.api)

    @cached_property
    def health(self):
        return HealthEndpoint(self.api)

    @cached_property
    def kv(self):
        return KVEndpoint(self.api)

    @cached_property
    def members(self):
        return MembersEndpoint(self.api)

    @cached_property
    def operator(self):
        return OperatorEndpoint(self.api)

    @cached_property
    def query(self):
        return QueryEndpoint(self.api)

    @cached_property
    def services(self):
        return ServicesEndpoint(self.api)

    @cached_property
    def session(self):
        return SessionEndpoint(self.api)

    @cached_property
    def status(self):
        return StatusEndpoint(self.api)

    def __repr__(self):
        return "<%s(%r)>" % (self.__class__.__name__, str(self.address))
