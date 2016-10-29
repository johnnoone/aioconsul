from .bases import EndpointBase
from aioconsul.api import consul, extract_meta
from aioconsul.exceptions import NotFound
from aioconsul.util import extract_attr


class SessionEndpoint(EndpointBase):
    """Create, destroy, and query sessions

    .. note:: All of the read session endpoints support blocking queries and
              all consistency modes.

    Session mechanism can be used to build distributed locks.
    Sessions act as a binding layer between nodes, health checks, and
    key/value data.
    """

    async def create(self, session, *, dc=None):
        """Creates a new session

        Parameters:
            session (Object): Session definition
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.

        Returns:
            Object: ID of the created session

        The create endpoint is used to initialize a new session.
        Sessions must be associated with a node and may be associated
        with any number of checks.

        The session object must look like::

            {
                "LockDelay": timedelta(seconds=15),
                "Name": "my-service-lock",
                "Node": "foobar",
                "Checks": ["a", "b", "c"],
                "Behavior": "release",
                "TTL": timedelta(seconds=0)
            }

        **LockDelay** can be specified as a duration string using a "s"
        suffix for seconds. The default is 15s.

        **Node** must refer to a node that is already registered, if specified.
        By default, the agent's own node name is used.

        **Name** can be used to provide a human-readable name for the Session.

        **Checks** is used to provide a list of associated health checks.
        It is highly recommended that, if you override this list, you include
        the default "serfHealth".

        **Behavior** can be set to either ``release`` or ``delete``.
        This controls the behavior when a session is invalidated.
        By default, this is ``release``, causing any locks that are held to be
        released. Changing this to ``delete`` causes any locks that are held
        to be deleted. ``delete`` is useful for creating ephemeral key/value
        entries.

        **TTL** field is a duration string, and like ``LockDelay`` it can use
        "s" as a suffix for seconds. If specified, it must be between 10s and
        86400s currently. When provided, the session is invalidated if it is
        not renewed before the TTL expires. The lowest practical TTL should be
        used to keep the number of managed sessions low.
        When locks are forcibly expired, such as during a leader election,
        sessions may not be reaped for up to double this TTL, so long TTL
        values (>1 hour) should be avoided.
        """
        response = await self._api.put(
            "/v1/session/create",
            data=session,
            params={"dc": dc})
        return response.body

    async def destroy(self, session, *, dc=None):
        """Destroys a given session

        Parameters:
            session (ObjectID): Session ID
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
        Returns:
            bool: ``True`` on success
        """
        session_id = extract_attr(session, keys=["ID"])
        response = await self._api.put("/v1/session/destroy", session_id,
                                       params={"dc": dc})
        return response.body is True

    delete = destroy

    async def info(self, session, *, dc=None, watch=None, consistency=None):
        """Queries a given session

        Parameters:
            session (ObjectID): Session ID
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            ObjectMeta: where value is the queried session
        Raises:
            NotFound: session is absent

        Returns the requested session information within a given datacenter.

        It returns a mapping like this::

            {
                "LockDelay": datetime.timedelta(0, 15),
                "Checks": [
                    "serfHealth"
                ],
                "Node": "foobar",
                "ID": "adf4238a-882b-9ddc-4a9d-5b6758e4159e",
                "CreateIndex": 1086449
            }
        """
        session_id = extract_attr(session, keys=["ID"])
        response = await self._api.get("/v1/session/info", session_id,
                                       watch=watch,
                                       consistency=consistency,
                                       params={"dc": dc})
        try:
            result = response.body[0]
        except IndexError:
            raise NotFound("No session for %r" % session_id)
        return consul(result, meta=extract_meta(response.headers))

    async def node(self, node, *, dc=None, watch=None, consistency=None):
        """Lists sessions belonging to a node

        Parameters:
            node (ObjectID): Node ID
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            CollectionMeta: where value is a list of
                                     sessions attached to node

        It returns a list like this::

            [
                {
                    "LockDelay": datetime.timedelta(0, 15),
                    "Checks": [
                        "serfHealth"
                    ],
                    "Node": "foobar",
                    "ID": "adf4238a-882b-9ddc-4a9d-5b6758e4159e",
                    "CreateIndex": 1086449
                },
                ...
            ]
        """
        node_id = extract_attr(node, keys=["Node", "ID"])
        response = await self._api.get("/v1/session/node", node_id, params={
            "dc": dc}, watch=watch, consistency=consistency)
        return consul(response)

    async def items(self, *, dc=None, watch=None, consistency=None):
        """Lists sessions

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            CollectionMeta: where value is a list of sessions

        It returns an object like this::

            [
                {
                    "LockDelay": datetime.timedelta(0, 15),
                    "Checks": [
                        "serfHealth"
                    ],
                    "Node": "foobar",
                    "ID": "adf4238a-882b-9ddc-4a9d-5b6758e4159e",
                    "CreateIndex": 1086449
                },
                ...
            ]
        """
        response = await self._api.get("/v1/session/list", params={
            "dc": dc}, watch=watch, consistency=consistency)
        return consul(response)

    async def renew(self, session, *, dc=None):
        """Renews a TTL-based session

        Parameters:
            session (ObjectID): Session ID
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
        Returns:
            ObjectMeta: where value is session
        Raises:
            NotFound: session is absent

        The response looks like this::

            {
                "LockDelay": datetime.timedelta(0, 15),
                "Checks": [
                    "serfHealth"
                ],
                "Node": "foobar",
                "ID": "adf4238a-882b-9ddc-4a9d-5b6758e4159e",
                "CreateIndex": 1086449
                "Behavior": "release",
                "TTL": datetime.timedelta(0, 15)
            }

        .. note:: Consul MAY return a TTL value higher than the one
                  specified during session creation. This indicates
                  the server is under high load and is requesting
                  clients renew less often.
        """
        session_id = extract_attr(session, keys=["ID"])
        response = await self._api.put("/v1/session/renew", session_id,
                                       params={"dc": dc})
        try:
            result = response.body[0]
        except IndexError:
            raise NotFound("No session for %r" % session_id)
        return consul(result, meta=extract_meta(response.headers))
