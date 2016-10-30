from .bases import EndpointBase


class StatusEndpoint(EndpointBase):
    """Get information about the status of the Consul cluster.

    .. note:: this information is generally very low level and not
               often useful for clients.
    """

    async def leader(self):
        """Returns the current Raft leader

        Returns:
            str: address of leader such as ``10.1.10.12:8300``
        """
        response = await self._api.get("/v1/status/leader")
        if response.status == 200:
            return response.body

    async def peers(self):
        """Returns the current Raft peer set

        Returns:
            Collection: addresses of peers

        This endpoint retrieves the Raft peers for the datacenter in which
        the agent is running. It returns a collection of addresses, such as::

            [
               "10.1.10.12:8300",
               "10.1.10.11:8300",
               "10.1.10.10:8300"
            ]

        This list of peers is strongly consistent and can be useful in
        determining when a given server has successfully joined the cluster.
        """
        response = await self._api.get("/v1/status/peers")
        if response.status == 200:
            return set(response.body)
