from .bases import EndpointBase
from aioconsul.util import extract_attr


class OperatorEndpoint(EndpointBase):

    async def configuration(self, *, dc=None, consistency=None):
        """Inspects the Raft configuration

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            consistency (str): Read the Raft configuration from any of the
                               Consul servers, otherwise raise an exception
                               if the cluster doesn't currently have a leader.
        Returns:
            Object:

        A JSON body is returned that looks like this::

            {
                "Servers": [
                    {
                        "ID": "127.0.0.1:8300",
                        "Node": "alice",
                        "Address": "127.0.0.1:8300",
                        "Leader": True,
                        "Voter": True
                    },
                    {
                        "ID": "127.0.0.2:8300",
                        "Node": "bob",
                        "Address": "127.0.0.2:8300",
                        "Leader": False,
                        "Voter": True
                    },
                    {
                        "ID": "127.0.0.3:8300",
                        "Node": "carol",
                        "Address": "127.0.0.3:8300",
                        "Leader": False,
                        "Voter": True
                    }
                ],
                "Index": 22
            }

        The **Servers** array has information about the servers in the
        Raft peer configuration:

        **ID** is the ID of the server. This is the same as the **Address**.

        **Node** is the node name of the server, as known to Consul, or
        "(unknown)" if the node is stale and not known.

        **Address** is the IP:port for the server.

        **Leader** is either ``True`` or ``False`` depending on the server's
        role in the Raft configuration.

        **Voter** is ``True`` or ``False``, indicating if the server has a
        vote in the Raft configuration. Future versions of Consul may add
        support for non-voting servers.

        The **Index** value is the Raft corresponding to this configuration.
        Note that the latest configuration may not yet be committed if changes
        are in flight.
        """
        response = await self._api.get("/v1/operator/raft/configuration",
                                       params={"dc": dc},
                                       consistency=consistency)
        return response.body

    async def peer_delete(self, *, dc=None, address):
        """Remove the server with given address from the Raft configuration

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            address (str): "IP:port" of the server to remove.
        Returns:
            bool: ``True`` on success

        There are rare cases where a peer may be left behind in the Raft
        configuration even though the server is no longer present and known
        to the cluster. This endpoint can be used to remove the failed server
        so that it is no longer affects the Raft quorum.
        """
        address = extract_attr(address, keys=["Address"])
        params = {"dc": dc, "address": address}
        response = await self._api.delete("/v1/operator/raft/peer",
                                          params=params)
        return response.status < 400
