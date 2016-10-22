Client Endpoints
================

.. currentmodule:: aioconsul.client

Common parameters
-----------------

:dc: By default, the datacenter of the agent is queried ;
     however, the dc can be provided.

:watch: Performs a blocking query. Value can be a :class:`ObjectIndex`,
        or a ``Tuple[ObjectIndex, timedelta]``.

:consistency: Change client behavior about consistency.
:session: A session Object.
:index: An index Object.
:token: A token Object.

Most of endpoints that returns ConsulValue supports blocking queries and
consistency modes.


.. _acl_endpoint:

ACL
---

Create, update, destroy, and query ACL tokens.

Most of the operations relies on ACL token with sufficant rights. Here is
the way aioconsul manage tokens::

    token = {"Name": "my-app-token"}
    token_id = await client.acl.create(token)
    token.update(token_id)
    token.update({"Rules": """
        key "" {
            policy = "read"
        }
        key "private/" {
            policy = "deny"
        }
    """})
    token_id = await client.acl.update(token)

    token, meta = await client.acl.info(token_id)
    clone_id, meta = await client.acl.clone(token_id)

    destroyed = await client.acl.destroy(token_id)

    tokens, meta = await client.acl.items()
    info = await client.acl.replication()

.. autoclass:: aioconsul.client.ACLEndpoint


.. _agent_endpoint:

Agent
-----

Interact with the local Consul agent.

Example::

    obj = await client.agent.info()
    disabled = await client.agent.disable(reason="migrating")
    enabled = await client.agent.enable(reason="migration done")

.. autoclass:: aioconsul.client.AgentEndpoint


.. _checks_endpoint:

Agent's Checks
--------------

Manage local checks.

Example::

    check = {
        "ID": "mem",
        "Name": "Memory utilization",
        "TTL": "15s"
        "Interval": "10s"
    }
    registered = await client.checks.register(check)
    mapping = await client.checks.items()
    marked = await client.checks.critical(check, note="Fatal")
    marked = await client.checks.warning(check, note="Warning")
    marked = await client.checks.passing(check, note="Back to normal")
    deregistered = await client.checks.deregister(check)

.. autoclass:: aioconsul.client.ChecksEndpoint


.. _members_endpoint:

Agent's Members
---------------

Manage local serf agent cluster

Example::

    joined = await client.checks.join("10.11.12.13", wan=True)
    members = await client.members.items()
    leaving = await client.checks.force_leave("my-node")

.. autoclass:: aioconsul.client.MembersEndpoint


.. _services_endpoint:

Agent's Services
----------------

Manage local services.

Example::

    service = {
        "ID": "redis1",
        "Name": "redis",
        "Tags": [
            "master",
            "v1"
        ],
    }
    registered = await client.services.register(service)
    services = await client.services.items()
    disabled = await client.services.disable(service, reason="migrating")
    enabled = await client.services.enable(service, reason="migration done")
    deregistered = await client.services.deregister(service)

.. autoclass:: aioconsul.client.ServicesEndpoint


.. _catalog_endpoint:

Catalog
-------

Manage catalog.

Example::

    definitions = {
      "Node": "foobar",
      "Address": "192.168.10.10",
      "Service": {
        "ID": "redis1",
        "Service": "redis",
        "Tags": [ "master", "v1" ],
        "Address": "127.0.0.1",
        "Port": 8000
      },
      "Check": {
        "Node": "foobar",
        "CheckID": "service:redis1",
        "Name": "Redis health check",
        "Notes": "Script based health check",
        "Status": "passing",
        "ServiceID": "redis1"
      }
    }

    registered = await client.catalog.register(definitions)
    datacenters = await client.catalog.datacenters()
    nodes, meta = await client.catalog.nodes(near="_self")
    services, meta = await client.catalog.node("foobar", watch=(meta, "30s"))
    services, meta = await client.catalog.services(consistency="stale")
    nodes, meta = await client.catalog.service("redis1", tag="prod")
    deregistered = await client.catalog.deregister({
        "Node": "foobar",
        "Address": "192.168.10.10"
    })

.. autoclass:: aioconsul.client.CatalogEndpoint


.. _event_endpoint:

Events
------

Manage events.

Example::

    id = await client.event.fire("my-event", service="my-service")
    collection, meta = await client.event.items("my-event")

.. autoclass:: aioconsul.client.EventEndpoint


.. _health_endpoint:

Health Checks
-------------

Consult health.

Example::

    collection, meta = await client.health.node("my-node")
    collection, meta = await client.health.checks("my-service")
    collection, meta = await client.health.state("passing", near="_self")

.. autoclass:: aioconsul.client.HealthEndpoint


.. _kv_endpoint:

Key/Value Store
---------------

Manage kv store.

Common operations example::

    keys, meta = await client.kv.keys("my/key", separator="/")
    setted = await client.kv.set("my/key", b"my value")
    obj, meta = await client.kv.get("my/key")
    deleted = await client.kv.delete("my/key")

Tree operations example::

    collection, meta = await client.kv.get_tree("my/key", separator="/")
    deleted = await client.kv.delete_tree("my/key", separator="/")

CAS operations example::

    setted = await client.kv.cas("my/key", b"my value", index=meta)
    deleted = await client.kv.delete_cas("my/key", index=meta)

Locked operations example::

    locked = await client.kv.lock("my/key", b"my value", session=session_id)
    unlocked = await client.kv.unlock("my/key", b"my value", session=session_id)

.. autoclass:: aioconsul.client.KVEndpoint


.. _kv_operations_endpoint:

Key/Value Transactions
----------------------

These same operations can be done in a transactional way::

    results, meta = await client.kv.prepare()\
                            .set("my/key", b"my value")\
                            .get("my/key")\
                            .execute()

.. autoclass:: aioconsul.client.KVOperations


.. _coordinate_endpoint:

Network Coordinates
-------------------

Consult network coordinates.

Example::

    datacenters = await client.coordinate.datacenters()
    collection, meta = await client.coordinate.nodes()

.. autoclass:: aioconsul.client.CoordinateEndpoint


.. _operator_endpoint:

Operator
--------

Manage raft.

Example::

    obj = await client.operator.configuration()
    obj = await client.operator.peer_delete("10.11.12.13")

.. autoclass:: aioconsul.client.OperatorEndpoint


.. _query_endpoint:

Prepared Queries
----------------

Manage prepared queries.

Example::

    collection = await client.query.items()
    obj = await client.query.create({""})
    obj = await client.query.read({""})
    obj = await client.query.explain({""})
    updated = await client.query.update({""})
    deleted = await client.query.delete({""})
    results = await client.query.execute({""})

.. autoclass:: aioconsul.client.QueryEndpoint


.. _session_endpoint:

Session
-------

Manage sessions.

Example::

    obj = await client.session.create({""})
    destroyed = await client.session.destroy({""})
    obj, meta = await client.session.info({""})
    obj, meta = await client.session.renew({""})
    collection, meta = await client.session.node("my-node")
    collection, meta = await client.session.items()

.. autoclass:: aioconsul.client.SessionEndpoint


.. _status_endpoint:

Status
------

Consult status.

Example::

  addr = await client.status.leader()
  addrs = await client.status.peers()

.. autoclass:: aioconsul.client.StatusEndpoint
