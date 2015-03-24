.. py:module:: aioconsul
.. _health:

Health
======

The Health endpoint is used to query health-related information.

Returns the health info of a node::

    >>> checks = yield from client.health(node='my.node')

Returns the checks of a service::

    >>> checks = yield from client.health(service='my.service')

Returns the nodes and health info of a service::

    >>> nodes = yield from client.health.nodes(service='my.service', tag='master')

Returns the checks in a given state::

    >>> checks = yield from client.health.items(state='passing')


Internals
---------

.. autoclass:: aioconsul.HealthEndpoint
   :members:
   :undoc-members:
