.. py:module:: aioconsul
.. _catalog:

Catalog
=======

The Catalog is the endpoint used to register and deregister nodes, services,
and checks. It also provides query endpoints. Most of the methods returns
:py:class:`asyncio.Task`.


Registering to the catalog
--------------------------

Returns datacenters::

    >>> dcs = yield from client.catalog.datacenters()

Register a node::

    >>> node = Node(address='my.address, port=6666)
    >>> success = yield from client.catalog.register(node)

Register a service to node::

    >>> service = NodeService('service.id', name='service.name')
    >>> success = yield from client.catalog.register(node, service=service)

Register a check to node::

    >>> check = Check('check.id', name='check.name', status='passing')
    >>> success = yield from client.catalog.register(node, check=check)


Requesting the catalog
----------------------

List datacenters::

    >>> dcs = yield from client.catalog.datacenters()

Get a node::

    >>> node = yield from client.catalog.get('my.node')

List all nodes::

    >>> nodes = yield from client.catalog.nodes()

List nodes filtered by service::

    >>> nodes = yield from client.catalog.nodes(service='my.service')

List services::

    >>> services = yield from client.catalog.services()


Watch changes
-------------

Wait for changes on nodes::

    >>> future = client.catalog.nodes(watch=meta)
    >>> future.add_done_callback(func)

Wait for changes on services::

    >>> future = client.catalog.services(watch=meta)
    >>> future.add_done_callback(func)


Datacenter
----------

By default, it will be requested to the agent dc.
You can wrap next requests to the specified datacenter.
The following example will fetch all nodes of `dc2`::

    >>> nodes = yield from client.catalog.dc('dc2').nodes()

Internals
---------

.. autoclass:: aioconsul.CatalogEndpoint
   :members:
   :undoc-members:
