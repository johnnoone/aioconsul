from .bases import EndpointBase
from aioconsul.util import extract_attr


class MembersEndpoint(EndpointBase):
    """Interact with the local Consul agent.
    """

    async def items(self, *, wan=None):
        """Returns the members as seen by the local serf agent

        Parameters:
            wan (bool): List of WAN members instead of the LAN members
        Returns:
            Collection: List of cluster's members

        This endpoint returns an object like::

            [
                {
                    "Name": "foobar",
                    "Addr": "10.1.10.12",
                    "Port": 8301,
                    "Tags": {
                        "bootstrap": "1",
                        "dc": "dc1",
                        "port": "8300",
                        "role": "consul"
                    },
                    "Status": 1,
                    "ProtocolMin": 1,
                    "ProtocolMax": 2,
                    "ProtocolCur": 2,
                    "DelegateMin": 1,
                    "DelegateMax": 3,
                    "DelegateCur": 3
                }
            ]
        """
        response = await self._api.get("/v1/agent/members",
                                       params={"wan": wan})
        return response.body

    async def join(self, address, *, wan=None):
        """Triggers the local agent to join a node

        Parameters:
            address (str): Address of node
            wan (bool): Attempt to join using the WAN pool
        Returns:
            bool: ``True`` on success

        This endpoint is used to instruct the agent to attempt to connect to
        a given address. For agents running in server mode, providing ``wan``
        parameter causes the agent to attempt to join using the WAN pool.
        """
        response = await self._api.get("/v1/agent/join", address,
                                       params={"wan": wan})
        return response.status == 200

    async def force_leave(self, node):
        """Forces removal of a node

        Parameters:
            node (ObjectID): Node name
        Returns:
            bool: ``True`` on success

        This endpoint is used to instruct the agent to force a node into the
        ``left`` state. If a node fails unexpectedly, then it will be in a
        ``failed`` state. Once in the ``failed`` state, Consul will attempt to
        reconnect, and the services and checks belonging to that node will not
        be cleaned up. Forcing a node into the ``left`` state allows its old
        entries to be removed.
        """
        node_id = extract_attr(node, keys=["Node", "ID"])
        response = await self._get("/v1/agent/force-leave", node_id)
        return response.status == 200
