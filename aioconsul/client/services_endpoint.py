from .bases import EndpointBase
from aioconsul.util import extract_attr


class ServicesEndpoint(EndpointBase):

    async def items(self):
        """Returns the services the local agent is managing

        Returns:
            Mapping: Mapping of services

        These services were either provided through configuration files or
        added dynamically using the HTTP API.

        This endpoint returns an object like this::

            {
                "redis": {
                    "ID": "redis",
                    "Service": "redis",
                    "Tags": None,
                    "Address": "",
                    "Port": 8000
                }
            }
        """
        response = await self._api.get("/v1/agent/services")
        return response.body

    async def register(self, service):
        """Registers a new local service.

        Returns:
            bool: ``True`` on success

        The register endpoint is used to add a new service,
        with an optional health check, to the local agent.

        The request body must look like::

            {
                "ID": "redis1",
                "Name": "redis",
                "Tags": [
                    "master",
                    "v1"
                ],
                "Address": "127.0.0.1",
                "Port": 8000,
                "EnableTagOverride": False,
                "Check": {
                    "DeregisterCriticalServiceAfter": timedelta(seconds=90),
                    "Script": "/usr/local/bin/check_redis.py",
                    "HTTP": "http://localhost:5000/health",
                    "Interval": timedelta(seconds=10),
                    "TTL": timedelta(seconds=15)
                }
            }

        The **Name** field is mandatory. If an **ID** is not provided,
        it is set to **Name**. You cannot have duplicate **ID** entries
        per agent, so it may be necessary to provide an **ID** in the case
        of a collision.

        **Tags**, **Address**, **Port**, **Check** and **EnableTagOverride**
        are optional.

        If **Address** is not provided or left empty, then the agent's
        address will be used as the address for the service during DNS
        queries. When querying for services using HTTP endpoints such
        as service health or service catalog and encountering an empty
        **Address** field for a service, use the **Address** field of
        the agent node associated with that instance of the service,
        which is returned alongside the service information.

        If **Check** is provided, only one of **Script**, **HTTP**, **TCP**
        or **TTL** should be specified. **Script** and **HTTP** also require
        **Interval**. The created check will be named "service:<ServiceId>".

        Checks that are associated with a service may also contain an
        optional **DeregisterCriticalServiceAfter** field, which is a timeout
        in the same format as **Interval** and **TTL**. If a check is in the
        critical state for more than this configured value, then its
        associated service (and all of its associated checks) will
        automatically be deregistered. The minimum timeout is 1 minute, and
        the process that reaps critical services runs every 30 seconds, so it
        may take slightly longer than the configured timeout to trigger the
        deregistration. This should generally be configured with a timeout
        that's much, much longer than any expected recoverable outage for the
        given service.

        **EnableTagOverride** can optionally be specified to disable the
        anti-entropy feature for this service's tags. If **EnableTagOverride**
        is set to ``True`` then external agents can update this service in the
        catalog and modify the tags. Subsequent local sync operations by this
        agent will ignore the updated tags. For instance, if an external agent
        modified both the tags and the port for this service and
        **EnableTagOverride** was set to true then after the next sync cycle
        the service's port would revert to the original value but the tags
        would maintain the updated value. As a counter example, if an external
        agent modified both the tags and port for this service and
        **EnableTagOverride** was set to false then after the next sync cycle
        the service's port and the tags would revert to the original value and
        all modifications would be lost. It's important to note that this
        applies only to the locally registered service. If you have multiple
        nodes all registering the same service their **EnableTagOverride**
        configuration and all other service configuration items are
        independent of one another. Updating the tags for the service
        registered on one node is independent of the same service (by name)
        registered on another node. If **EnableTagOverride** is not specified
        the default value is ``False``.
        """
        response = await self._api.put("/v1/agent/service/register",
                                       json=service)
        return response.status == 200

    async def deregister(self, service):
        """Deregisters a local service

        Parameters:
            service (ObjectID): Service ID
        Returns:
            bool: ``True`` on success

        The deregister endpoint is used to remove a service from the local
        agent. The agent will take care of deregistering the service with the
        Catalog. If there is an associated check, that is also deregistered.
        """
        service_id = extract_attr(service, keys=["ServiceID", "ID"])
        response = await self._api.get(
            "/v1/agent/service/deregister", service_id)
        return response.status == 200

    async def disable(self, service, *, reason=None):
        """Enters maintenance mode for service

        Parameters:
            service (ObjectID): Service ID
            reason (str): Text string explaining the reason for placing the
                          service into maintenance mode.
        Returns:
            bool: ``True`` on success

        Places a given service into "maintenance mode".
        During maintenance mode, the service will be marked as unavailable
        and will not be present in DNS or API queries.

        Maintenance mode is persistent and will be automatically restored on
        agent restart.
        """
        return await self.maintenance(service, False, reason=reason)

    async def enable(self, service, *, reason=None):
        """Resumes normal operation for service

        Parameters:
            service (ObjectID): Service ID
            reason (str): Text string explaining the reason for placing the
                          service into normal mode.
        Returns:
            bool: ``True`` on success
        """
        return await self.maintenance(service, False, reason=reason)

    async def maintenance(self, service, enable, *, reason=None):
        """Enters maintenance mode / Resumes normal operation for service

        Parameters:
            service (ObjectID): Service ID
            enable (bool): Enter or exit maintenance mode
            reason (str): Text string explaining the reason for placing the
                          service into normal mode.
        Returns:
            bool: ``True`` on success
        """
        service_id = extract_attr(service, keys=["ServiceID", "ID"])
        response = await self._api.put(
            "/v1/agent/service/maintenance", service_id,
            params={"enable": enable, "reason": reason})
        return response.status == 200
