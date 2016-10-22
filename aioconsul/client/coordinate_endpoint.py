from .bases import EndpointBase
from aioconsul.structures import consul


class CoordinateEndpoint(EndpointBase):
    """The Coordinate endpoint is used to query for the network coordinates
    for nodes in the local datacenter as well as Consul servers in the local
    datacenter and remote datacenters.

    See the Network Coordinates internals guide for more information on
    how these coordinates are computed, and for details on how to perform
    calculations with them.
    """

    async def datacenters(self):
        """Queries for WAN coordinates of Consul servers

        Returns:
            Mapping: WAN network coordinates for all Consul
                     servers, organized by DCs.

        It returns a body like this::

            {
                "dc1": {
                    "Datacenter": "dc1",
                    "Coordinates": [
                        {
                            "Node": "agent-one",
                            "Coord": {
                                "Adjustment": 0,
                                "Error": 1.5,
                                "Height": 0,
                                "Vec": [0,0,0,0,0,0,0,0]
                            }
                        }
                    ]
                }
            }

        This endpoint serves data out of the server's local Serf data about
        the WAN, so its results may vary as requests are handled by different
        servers in the cluster.

        Also, it does not support blocking queries or any consistency modes.
        """
        response = await self._api.get("/v1/coordinate/datacenters")
        return {data["Datacenter"]: data for data in response.body}

    async def nodes(self, *, dc=None, watch=None, consistency=None):
        """Queries for LAN coordinates of Consul nodes

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): do a blocking query
            consistency (Consistency): force consistency
        Returns:
            CollectionMeta: where value is a list of node / coord

        This endpoint is hit with a GET and returns the LAN network
        coordinates for all nodes in a given DC.
        By default, the datacenter of the agent is queried.

        It returns a body like this::

            [
                {
                    "Node": "agent-one",
                    "Coord": {
                        "Adjustment": 0,
                        "Error": 1.5,
                        "Height": 0,
                        "Vec": [0,0,0,0,0,0,0,0]
                    }
                }
            ]
        """
        path = "/v1/coordinate/nodes"
        response = await self._api.get(path, params={
            "dc": dc}, watch=watch, consistency=consistency)
        return consul(response)
