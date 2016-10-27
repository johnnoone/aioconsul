from .bases import EndpointBase
from aioconsul.util import extract_attr


class ChecksEndpoint(EndpointBase):

    async def items(self):
        """Returns the checks the local agent is managing

        Returns:
            Mapping: Mapping of checks

        These checks were either provided through configuration files
        or added dynamically using the HTTP API.

        This endpoint returns an object like this::

            {
                "service:redis": {
                    "Node": "foobar",
                    "CheckID": "service:redis",
                    "Name": "Service 'redis' check",
                    "Status": "passing",
                    "Notes": "",
                    "Output": "",
                    "ServiceID": "redis",
                    "ServiceName": "redis"
                }
            }
        """
        response = await self._api.get("/v1/agent/checks")
        return response.body

    async def register(self, check, *, token=None):
        """Registers a new local check

        Parameters:
            check (Object): Check definition
            token (ObjectID): Token ID
        Returns:
            bool: ``True`` on success

        The register endpoint is used to add a new check to the local agent.
        Checks may be of script, HTTP, TCP, or TTL type. The agent is
        responsible for managing the status of the check and keeping the
        Catalog in sync.

        The request body must look like::

            {
                "ID": "mem",
                "Name": "Memory utilization",
                "Notes": "Ensure we don't oversubscribe memory",
                "DeregisterCriticalServiceAfter": "90m",
                "Script": "/usr/local/bin/check_mem.py",
                "DockerContainerID": "f972c95ebf0e",
                "Shell": "/bin/bash",
                "HTTP": "http://example.com",
                "TCP": "example.com:22",
                "Interval": timedelta(seconds=10),
                "TTL": timedelta(seconds=15)
            }

        The **Name** field is mandatory, as is one of **Script**, **HTTP**,
        **TCP** or **TTL**. **Script**, **TCP** and **HTTP** also require that
        **Interval** be set.

        If an **ID** is not provided, it is set to **Name**. You cannot have
        duplicate **ID** entries per agent, so it may be necessary to provide
        an **ID**.

        The **Notes** field is not used internally by Consul and is meant to
        be human-readable.

        Checks that are associated with a service may also contain an optional
        **DeregisterCriticalServiceAfter** field, which is a timeout in the
        same duration format as **Interval** and **TTL**. If a check is in the
        critical state for more than this configured value, then its
        associated service (and all of its associated checks) will
        automatically be deregistered. The minimum timeout is 1 minute, and
        the process that reaps critical services runs every 30 seconds, so it
        may take slightly longer than the configured timeout to trigger the
        deregistration. This should generally be configured with a timeout
        that's much, much longer than any expected recoverable outage for the
        given service.

        If a **Script** is provided, the check type is a script, and Consul
        will evaluate the script every **Interval** to update the status.

        If a **DockerContainerID** is provided, the check is a Docker check,
        and Consul will evaluate the script every **Interval** in the given
        container using the specified Shell. Note that Shell is currently only
        supported for Docker checks.

        An **HTTP** check will perform an HTTP GET request against the value of
        **HTTP** (expected to be a URL) every **Interval**. If the response is
        any 2xx code, the check is passing. If the response is
        ``429 Too Many Requests``, the check is **warning**.
        Otherwise, the check is **critical**.

        An **TCP** check will perform an TCP connection attempt against the
        value of **TCP** (expected to be an IP/hostname and port combination)
        every **Interval**. If the connection attempt is successful, the check
        is **passing**. If the connection attempt is unsuccessful, the check
        is **critical**. In the case of a hostname that resolves to both IPv4
        and IPv6 addresses, an attempt will be made to both addresses, and the
        first successful connection attempt will result in a successful check.

        If a **TTL** type is used, then the TTL update endpoint must be used
        periodically to update the state of the check.

        The **ServiceID** field can be provided to associate the registered
        check with an existing service provided by the agent.

        The **Status** field can be provided to specify the initial state of
        the health check.
        """
        token_id = extract_attr(token, keys=["ID"])
        params = {"token": token_id}
        response = await self._api.put("/v1/agent/check/register",
                                       params=params,
                                       json=check)
        return response.status == 200

    async def deregister(self, check):
        """Deregisters a local check

        Parameters:
            check (ObjectID): Check ID
        Returns:
            bool: ``True`` on success

        The agent will take care of deregistering the check from the Catalog.
        """
        check_id = extract_attr(check, keys=["CheckID", "ID"])
        response = await self._api.get("/v1/agent/check/deregister", check_id)
        return response.status == 200

    async def passing(self, check, *, note=None):
        """Marks a local check as passing

        Parameters:
            note (str): Associate a human-readable message with the status
                        of the check
        Returns:
            bool: ``True`` on success
        """
        return await self.mark(check, "passing", note=note)

    async def warning(self, check, *, note=None):
        """Marks a local check as warning

        Parameters:
            note (str): Associate a human-readable message with the status
                        of the check
        Returns:
            bool: ``True`` on success
        """
        return await self.mark(check, "warning", note=note)

    async def critical(self, check, *, note=None):
        """Marks a local check as critical

        Parameters:
            note (str): Associate a human-readable message with the status
                        of the check
        Returns:
            bool: ``True`` on success
        """
        return await self.mark(check, "critical", note=note)

    async def mark(self, check, status, *, note=None):
        """Marks a local check as passing, warning or critical
        """
        check_id = extract_attr(check, keys=["CheckID", "ID"])
        data = {
            "Status": status,
            "Output": note
        }
        response = await self._api.put("/v1/agent/check/update", check_id,
                                       json=data)
        return response.status == 200
