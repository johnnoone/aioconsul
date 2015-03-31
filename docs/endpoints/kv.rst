.. py:module:: aioconsul
.. _kv:

KV
==

The KV endpoint is used to access Consul's simple key/value store, useful for
storing service configuration or other metadata. Almost every methods returns
:ref:`asyncio.Tasks`, and results and exceptions implements a `consul`
attribute which holds `meta data`_.

Simple usage
------------

Set a value::

    >>> setted = yield from client.kv.set('my/key', 'bar')
    >>> assert setted

Get a value::

    >>> value = yield from client.kv.get('my/key')

Delete a value::

    >>> deleted = yield from client.kv.delete('my/key')
    >>> assert deleted

Fetch all values by prefix::

    >>> values = yield from client.kv.items('my/prefix/')

Fetch all keys by prefix::

    >>> keys = yield from client.kv.keys('my/prefix/')


Acquired keys
-------------

Consul allows to acquire/release keys, with a session has returned by the :ref:`session` endpoint::

    >>> session = yield from client.session.create()
    >>> created = yield from client.kv.set('my/key', 'bar')
    >>> acquired = yield from client.kv.acquire('my/key', session=session)
    >>> assert acquired
    >>> released = yield from client.kv.release('my/key', session=session)
    >>> assert released


Meta data
---------

Meta holds some informations, like last_index...

They are stored into the `consul` attribute of returned objects::

    >>> value = yield from client.kv.get('my/key')
    >>> meta = value.consul  # key meta

Or::

    >>> keys = yield from client.kv.keys('foo/')
    >>> meta = keys.consul  # headers meta

They can also be fetched via the :meth:`~aioconsul.KVEndpoint.meta` method::

    >>> meta = yield from client.kv.meta('my/key')
    >>> meta = yield from client.kv.meta(prefix='my/prefix')


Playing with CAS
----------------

CAS (or check and set) is a special keyword for concurrent operations. You can use the meta object as a CAS.

For example, in case of a set, put, etc.::

    >>> setted = yield from client.key.get('my/key', 'bar', cas=meta)
    >>> assert setted

Or delete operations::

    >>> deleted = yield from client.key.delete('my/key', cas=meta)
    >>> assert deleted


Watch
-----

AIOConsul implements key watching::

    >>> future = client.kv.get('my/key' watch=meta)
    >>> future.add_done_callback(fun)

And prefix watching::

    >>> future = client.kv.items('my/key', watch=meta)
    >>> future.add_done_callback(fun)


Datacenter
----------

By convention, consul will performs its query to the node dc.
You can wrap next requests to the specified datacenter.
The following example will fetch all values of `dc2`::

    >>> sessions = yield from client.kv.dc('dc2').items('foo/bar')


Internals
---------

.. autoclass:: aioconsul.KVEndpoint
   :members:
   :undoc-members:
