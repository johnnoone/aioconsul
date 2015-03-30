.. py:module:: aioconsul
.. _health:

Health
======

The Health endpoint is used to query health-related information.


Health checks
-------------

Returns the checks info of a node::

    >>> checks = yield from client.health(node='my.node')

Returns the checks of a service::

    >>> checks = yield from client.health(service='my.service')

Returns the checks in a given state::

    >>> checks = yield from client.health(state='passing')

These kind of queries return a :class:`DataSet` of :class:`Check`.


Health nodes
------------

Returns the nodes and health info that belongs to a service::

    >>> nodes = yield from client.health.nodes(service='my.service',
    >>>                                        tag='master')

This query returns a :class:`DataSet` of :class:`Node`.
:class:`Node` instances have two specials attributes:

* `service` which holds an instance of :class:`NodeService`
* `checks` which holds instances of :class:`Check`

.. note::

    Loop thru Node returns the :class:`NodeService` instance::

        >>> for node in nodes:
        >>>     for service in node:
        >>>         assert isinstance(service, NodeService)


Internals
---------

.. autoclass:: aioconsul.HealthEndpoint
   :members:
   :undoc-members:
