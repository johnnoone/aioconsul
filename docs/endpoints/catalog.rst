.. py:module:: aioconsul
.. _catalog:

Catalog
=======

The Catalog is the endpoint used to register and deregister nodes, services, and checks. It also provides query endpoints

You can also wrap next requests to the specified datacenter.
The following example will fetch all nodes of `dc2`::

    >>> sessions = yield from client.catalog.dc('dc2').nodes()

Internals
---------

.. autoclass:: aioconsul.CatalogEndpoint
   :members:
   :undoc-members:
