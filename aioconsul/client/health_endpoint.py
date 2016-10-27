from .bases import EndpointBase
from aioconsul.api import consul
from aioconsul.util import extract_attr


class HealthEndpoint(EndpointBase):
    """Health Checks

    The Health endpoints are used to query health-related information.
    They are provided separately from the Catalog since users may prefer not
    to use the optional health checking mechanisms. Additionally, some of the
    query results from the Health endpoints are filtered while the Catalog
    endpoints provide the raw entries.
    """

    async def node(self, node, *, dc=None, watch=None, consistency=None):
        """Returns the health info of a node.

        Parameters:
            node (ObjectID): Node ID
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            CollectionMeta: where value is a list of checks

        returns the checks specific of a node.

        It returns a body like this::

            [
              {
                "Node": "foobar",
                "CheckID": "serfHealth",
                "Name": "Serf Health Status",
                "Status": "passing",
                "Notes": "",
                "Output": "",
                "ServiceID": "",
                "ServiceName": ""
              },
              {
                "Node": "foobar",
                "CheckID": "service:redis",
                "Name": "Service 'redis' check",
                "Status": "passing",
                "Notes": "",
                "Output": "",
                "ServiceID": "redis",
                "ServiceName": "redis"
              }
            ]

        In this case, we can see there is a system level check (that is, a
        check with no associated ``ServiceID``) as well as a service check for
        Redis. The "serfHealth" check is special in that it is automatically
        present on every node. When a node joins the Consul cluster, it is
        part of a distributed failure detection provided by Serf. If a node
        fails, it is detected and the status is automatically changed to
        ``critical``.
        """
        node_id = extract_attr(node, keys=["Node", "ID"])

        params = {"dc": dc}
        response = await self._api.get("/v1/health/node", node_id,
                                       params=params,
                                       watch=watch,
                                       consistency=consistency)
        return consul(response)

    async def checks(self, service, *,
                     dc=None, near=None, watch=None, consistency=None):
        """Returns the checks of a service

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            near (str): With a node name will sort the node list in ascending
                        order based on the estimated round trip time from that
                        node
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            CollectionMeta: where value is a list of checks
        """
        service_id = extract_attr(service, keys=["ServiceID", "ID"])
        params = {"dc": dc, "near": near}
        response = await self._api.get("/v1/health/checks", service_id,
                                       params=params,
                                       watch=watch,
                                       consistency=consistency)
        return consul(response)

    async def service(self, service, *,
                      dc=None, near=None, tag=None, passing=None,
                      watch=None, consistency=None):
        """Returns the nodes and health info of a service

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            near (str): With a node name will sort the node list in ascending
                        order based on the estimated round trip time from that
                        node
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            CollectionMeta: where value is a list of nodes
        """
        service_id = extract_attr(service, keys=["ServiceID", "ID"])
        params = {
            "dc": dc,
            "near": near,
            "tag": tag,
            "passing": passing}
        response = await self._api.get("/v1/health/service", service_id,
                                       params=params,
                                       watch=watch,
                                       consistency=consistency)
        return consul(response)

    async def state(self, state, *,
                    dc=None, near=None, watch=None, consistency=None):
        """Returns the checks in a given state

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            near (str): With a node name will sort the node list in ascending
                        order based on the estimated round trip time from that
                        node
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            ObjectMeta: where value is a list of checks

        returns the checks in the state provided on the path.
        By default, the datacenter of the agent is queried; however,
        the dc can be provided using the "?dc=" query parameter.

        Adding the optional "?near=" parameter with a node name will sort
        the node list in ascending order based on the estimated round
        trip time from that node. Passing "?near=_agent" will use the
        agent's node for the sort.

        The supported states are any, passing, warning, or critical.
        The any state is a wildcard that can be used to return all checks.

        It returns a body like this::

            [
              {
                "Node": "foobar",
                "CheckID": "serfHealth",
                "Name": "Serf Health Status",
                "Status": "passing",
                "Notes": "",
                "Output": "",
                "ServiceID": "",
                "ServiceName": ""
              },
              {
                "Node": "foobar",
                "CheckID": "service:redis",
                "Name": "Service 'redis' check",
                "Status": "passing",
                "Notes": "",
                "Output": "",
                "ServiceID": "redis",
                "ServiceName": "redis"
              }
            ]
        """
        params = {"dc": dc, "near": near}
        response = await self._api.get("/v1/health/state", state,
                                       params=params,
                                       watch=watch,
                                       consistency=consistency)
        return consul(response)
