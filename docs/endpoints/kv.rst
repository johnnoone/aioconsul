.. py:module:: aioconsul
.. _kv:

KV
==

The KV endpoint is used to access Consul's simple key/value store, useful for
storing service configuration or other metadata.

You can also wrap next requests to the specified datacenter.
The following example will fetch all values of `dc2`::

    >>> sessions = yield from client.kv.dc('dc2').items('foo/bar')


Internals
---------

.. autoclass:: aioconsul.KVEndpoint
   :members:
   :undoc-members:
