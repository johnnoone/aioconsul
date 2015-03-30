.. py:module:: aioconsul
.. _kv:

KV
==

The KV endpoint is used to access Consul's simple key/value store, useful for
storing service configuration or other metadata.

Simple usage
------------

Set a value::

    >>> setted = yield from client.kv.set('foo', bar')
    >>> assert setted

Get a value::

    >>> value = yield from client.kv.get('foo')

Delete a value::

    >>> deleted = yield from client.kv.delete('foo')
    >>> assert deleted

Fetch all values by prefix::

    >>> values = yield from client.kv.items('my/prefix/')

Fetch all keys by prefix::

    >>> keys = yield from client.kv.keys('my/prefix/')


Acquired keys
-------------

Consul allows to acquire/release keys, with a session has returned by the :ref:`session` endpoint::

    >>> session = yield from client.session.create()
    >>> created = yield from client.kv.set('foo', 'bar')
    >>> acquired = yield from client.kv.acquire('foo', session=session)
    >>> assert acquired
    >>> released = yield from client.kv.release('foo', session=session)
    >>> assert released


Playing with CAS
----------------

CAS (or check and set) is a special keyword for atomic operations.

The CAS id corresponds to the modified_index of :class:`Key` object, last_index of :class:`ConsulMeta`.

There is two ways to get the "meta"::

    >>> value = yield from client.key.get('foo')
    >>> meta = value.consul  # our meta

Or:

    >>> keys = yield from client.key.keys('foo/')
    >>> meta = keys.consul  # another meta

Then you can use this meta instance in some kv operations.
For example, in case of a set, put, etc.::

    >>> setted = yield from client.key.get('foo', 'bar', cas=meta)
    >>> assert setted

Or into delete operations::

    >>> deleted = yield from client.key.delete('foo', cas=meta)
    >>> assert deleted


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
