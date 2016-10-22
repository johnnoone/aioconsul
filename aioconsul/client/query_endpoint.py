from .bases import EndpointBase
from aioconsul.common import extract_id


class QueryEndpoint(EndpointBase):
    """Create, update, destroy, and execute prepared queries.

    Prepared queries allow you to register a complex service query and then
    execute it later via its ID or name to get a set of healthy nodes that
    provide a given service. This is particularly useful in combination with
    Consul's DNS Interface as it allows for much richer queries than would be
    possible given the limited entry points exposed by DNS.
    """

    async def items(self, *, dc=None, watch=None, consistency=None):
        """Provides a listing of all prepared queries

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): do a blocking query
            consistency (Consistency): force consistency
        Returns:
            Collection: List of prepared queries

        This returns a list of prepared queries, which looks like::

            [
                {
                    "ID": "8f246b77-f3e1-ff88-5b48-8ec93abf3e05",
                    "Name": "my-query",
                    "Session": "adf4238a-882b-9ddc-4a9d-5b6758e4159e",
                    "Token": "<hidden>",
                    "Service": {
                        "Service": "redis",
                        "Failover": {
                            "NearestN": 3,
                            "Datacenters": ["dc1", "dc2"]
                        },
                        "OnlyPassing": False,
                        "Tags": ["master", "!experimental"]
                    },
                    "DNS": {
                        "TTL": timedelta(seconds=10)
                    },
                    "RaftIndex": {
                        "CreateIndex": 23,
                        "ModifyIndex": 42
                    }
                }
            ]
        """
        response = await self._api.get("/v1/query", params={"dc": dc})
        return response.body

    async def create(self, query, *, dc=None):
        """Creates a new prepared query

        Parameters:
            Query (Object): Query definition
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
        Returns:
            Object: New query ID

        The create operation expects a body that defines the prepared query,
        like this example::

            {
                "Name": "my-query",
                "Session": "adf4238a-882b-9ddc-4a9d-5b6758e4159e",
                "Token": "",
                "Near": "node1",
                "Service": {
                    "Service": "redis",
                    "Failover": {
                        "NearestN": 3,
                        "Datacenters": ["dc1", "dc2"]
                    },
                    "OnlyPassing": False,
                    "Tags": ["master", "!experimental"]
                },
                "DNS": {
                    "TTL": timedelta(seconds=10)
                }
            }

        Only the **Service** field inside the **Service** structure is
        mandatory, all other fields will take their default values if they
        are not included.

        **Name** is an optional friendly name that can be used to execute a
        query instead of using its ID.

        **Session** provides a way to automatically remove a prepared query
        when the given session is invalidated. This is optional, and if not
        given the prepared query must be manually removed when no longer
        needed.

        **Token**, if specified, is a captured ACL Token that is reused as the
        ACL Token every time the query is executed. This allows queries to be
        executed by clients with lesser or even no ACL Token, so this should
        be used with care. The token itself can only be seen by clients with a
        management token. If the **Token** field is left blank or omitted, the
        client's ACL Token will be used to determine if they have access to the
        service being queried. If the client does not supply an ACL Token, the
        anonymous token will be used.

        **Near** allows specifying a particular node to sort near based on
        distance sorting using Network Coordinates. The nearest instance to
        the specified node will be returned first, and subsequent nodes in the
        response will be sorted in ascending order of estimated round-trip
        times. If the node given does not exist, the nodes in the response
        will be shuffled. Using the magic **_agent** value is supported, and
        will automatically return results nearest the agent servicing the
        request. If unspecified, the response will be shuffled by default.

        The set of fields inside the **Service** structure define the
        query's behavior.

        **Service** is the name of the service to query. This is required.

        **Failover** contains two fields, both of which are optional, and
        determine what happens if no healthy nodes are available in the local
        datacenter when the query is executed. It allows the use of nodes in
        other datacenters with very little configuration.

        If **NearestN** is set to a value greater than zero, then the query
        will be forwarded to up to **NearestN** other datacenters based on
        their estimated network round trip time using Network Coordinates from
        the WAN gossip pool. The median round trip time from the server
        handling the query to the servers in the remote datacenter is used to
        determine the priority. The default value is zero. All Consul servers
        must be running version 0.6.0 or above in order for this feature to
        work correctly. If any servers are not running the required version of
        Consul they will be considered last since they won't have any
        available network coordinate information.

        **Datacenters** contains a fixed list of remote datacenters to forward
        the query to if there are no healthy nodes in the local datacenter.
        Datacenters are queried in the order given in the list. If this option
        is combined with **NearestN**, then the **NearestN** queries will be
        performed first, followed by the list given by **Datacenters**. A
        given datacenter will only be queried one time during a failover, even
        if it is selected by both **NearestN** and is listed in
        **Datacenters**. The default value is an empty list.

        **OnlyPassing** controls the behavior of the query's health check
        filtering. If this is set to false, the results will include nodes
        with checks in the passing as well as the warning states. If this is
        set to true, only nodes with checks in the passing state will be
        returned. The default value is False.

        **Tags** provides a list of service tags to filter the query results.
        For a service to pass the tag filter it must have all of the required
        tags, and none of the excluded tags (prefixed with ``!``).
        The default value is an empty list, which does no tag filtering.

        **TTL** in the **DNS** structure is a duration string that can use "s"
        as a suffix for seconds. It controls how the TTL is set when query
        results are served over DNS. If this isn't specified, then the Consul
        agent configuration for the given service will be used
        (see DNS Caching). If this is specified, it will take precedence over
        any Consul agent-specific configuration. If no TTL is specified here
        or at the Consul agent level, then the TTL will default to 0.

        It returns the ID of the created query::

            {
                "ID": "8f246b77-f3e1-ff88-5b48-8ec93abf3e05"
            }
        """
        response = await self._api.post("/v1/query",
                                        params={"dc": dc}, json=query)
        return response.body

    async def read(self, query, *, dc=None, watch=None, consistency=None):
        """Fetches existing prepared query

        Parameters:
            query (ObjectID): Query ID
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): do a blocking query
            consistency (Consistency): force consistency
        Returns:
            Object: Query definition
        Raises:
            NotFound: Query does not exist
        """
        query_id = extract_id(query)

        response = await self._api.get("/v1/query", query_id, params={
            "dc": dc}, watch=watch, consistency=consistency)
        result = response.body[0]
        return result

    async def update(self, query, *, dc=None):
        """Updates existing prepared query

        Parameters:
            Query (Object): Query definition
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
        Returns:
            bool: ``True`` on success
        """
        query_id = extract_id(query)
        response = await self._api.put("/v1/query", query_id,
                                       params={"dc": dc}, json=query)
        return response.status == 200

    async def delete(self, query, *, dc=None):
        """Delete existing prepared query

        Parameters:
            query (ObjectID): Query ID
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
        Results:
            bool: ``True`` on success
        """
        query_id = extract_id(query)
        response = await self._api.delete("/v1/query", query_id,
                                          params={"dc": dc})
        return response.status == 200

    async def execute(self, query, *,
                      dc=None, near=None, limit=None, consistency=None):
        """Executes a prepared query

        Parameters:
            query (ObjectID): Query ID
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            near (str): Sort the resulting list in ascending order based on
                        the estimated round trip time from that node
            limit (int): limit the list's size to the given number of nodes
            consistency (Consistency): force consistency
        Returns:
            Object:
        Raises:
            NotFound: the query does not exist

        Returns a body like this::

            {
                "Service": "redis",
                "Nodes": [
                    {
                        "Node": {
                            "Node": "foobar",
                            "Address": "10.1.10.12",
                            "TaggedAddresses": {
                                "lan": "10.1.10.12",
                                "wan": "10.1.10.12"
                            }
                        },
                        "Service": {
                            "ID": "redis",
                            "Service": "redis",
                            "Tags": None,
                            "Port": 8000
                        },
                        "Checks": [
                            {
                                "Node": "foobar",
                                "CheckID": "service:redis",
                                "Name": "Service 'redis' check",
                                "Status": "passing",
                                "Notes": "",
                                "Output": "",
                                "ServiceID": "redis",
                                "ServiceName": "redis"
                            },
                            {
                                "Node": "foobar",
                                "CheckID": "serfHealth",
                                "Name": "Serf Health Status",
                                "Status": "passing",
                                "Notes": "",
                                "Output": "",
                                "ServiceID": "",
                                "ServiceName": ""
                            }
                        ],
                        "DNS": {
                            "TTL": timedelta(seconds=10)
                        },
                        "Datacenter": "dc3",
                        "Failovers": 2
                    }
                ]
            }

        The **Nodes** section contains the list of healthy nodes providing
        the given service, as specified by the constraints of the prepared
        query.

        **Service** has the service name that the query was selecting. This is
        useful for context in case an empty list of nodes is returned.

        **DNS** has information used when serving the results over DNS. This
        is just a copy of the structure given when the prepared query was
        created.

        **Datacenter** has the datacenter that ultimately provided the list of
        nodes and **Failovers** has the number of remote datacenters that were
        queried while executing the query. This provides some insight into
        where the data came from. This will be zero during non-failover
        operations where there were healthy nodes found in the local
        datacenter.
        """
        query_id = extract_id(query)
        response = await self._api.get(
            "/v1/query/%s/execute" % query_id,
            params={"dc": dc, "near": near, "limit": limit},
            consistency=consistency)
        return response.body

    async def explain(self, query, *, dc=None, consistency=None):
        """Fetches existing prepared query

        Parameters:
            query (ObjectID): Query ID
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): do a blocking query
            consistency (Consistency): force consistency
        Returns:
            Object: the query
        Raises:
            NotFound: the query does not exist
        """
        query_id = extract_id(query)
        path = "/v1/query/%s/explain" % query_id
        response = await self._api.get(path, consistency=consistency, params={
            "dc": dc})
        result = response.body
        return result
