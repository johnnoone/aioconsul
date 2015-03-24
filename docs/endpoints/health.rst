.. py:module:: aioconsul
.. _health:

Health
======

The Health endpoints are used to query health-related information. They are provided separately from the Catalog since users may prefer not to use the optional health checking mechanisms. Additionally, some of the query results from the Health endpoints are filtered while the Catalog endpoints provide the raw entries.

The following endpoints are supported:

Returns the health info of a node::

    >>> checks = yield from client.health.node('my.node')

Returns the checks of a service::

    >>> checks = yield from client.health.checks('my.service')

Returns the nodes and health info of a service::

    >>> nodes = yield from client.health.service('my.service', tag='master')

Returns the checks in a given state::

    >>> checks = yield from client.health.state('passing')


Internals
---------

.. autoclass:: aioconsul.HealthEndpoint
   :members:
   :undoc-members:
