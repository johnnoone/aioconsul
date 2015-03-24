.. py:module:: aioconsul
.. _agent:

Agent
=====

The Agent endpoints are used to interact with the local Consul agent. Usually, services and checks are registered with an agent which then takes on the burden of keeping that data synchronized with the cluster.

The following endpoints are supported:

Returns the checks the local agent is managing::

    >>> yield from client.agent.checks()

Returns the services the local agent is managing::

    >>> yield from client.agent.services()

Returns the members as seen by the local serf agent::

    >>> members = yield from client.agent.members()

Returns the local node configuration::

    >>> yield from client.agent.config()

Manages node maintenance mode::

    >>> yield from client.agent.disable()
    >>> yield from client.agent.enable()

Triggers the local agent to join a node::

    >>> yield from client.agent.join('other.node.ip')

Forces removal of a node::

    >>> yield from client.agent.force_leave('other.node.ip')

Registers a new local check::

    >>> check = yield from client.agent.checks.register_ttl('my-ttl-check')

Registers a new local service::

    >>> service = yield from client.agent.services.register('my-service')

Disable a local service::

    >>> yield from client.agent.services.disable(service)

Etc...

Internals
---------

.. autoclass:: aioconsul.AgentEndpoint
   :members:
   :undoc-members:

.. autoclass:: aioconsul.AgentCheckEndpoint
   :members:
   :undoc-members:

.. autoclass:: aioconsul.AgentServiceEndpoint
   :members:
   :undoc-members:
