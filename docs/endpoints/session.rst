.. py:module:: aioconsul
.. _session:

Session
=======

The Session endpoint is used to create, destroy, and query sessions. The following endpoints are supported.

Create a session::

    >>> created = yield from client.sessions.create(name='foo',
    >>>                                             node='my.node.name',
    >>>                                             ttl='60s')

Fetch this session::

    >>> session = yield from client.sessions.get(created)
    >>> assert created == session  # they are the same

List all attached sessions of datacenter::

    >>> sessions = yield from client.sessions()
    >>> assert session in sessions  # my session is in the list

List all attached sessions of datacenter, but filtered by my node::

    >>> sessions = yield from client.sessions(node='my.node.name')

I'm done with it, delete my session::

    >>> deleted = yield from client.sessions.delete(session)
    >>> assert deleted  # my session does not exists anymore

You can also wrap next requests to the specified datacenter. 
The following example will fetch all sessions of `dc2`::

    >>> sessions = yield from client.sessions.dc('dc2').items()


Internals
---------

.. autoclass:: aioconsul.SessionEndpoint
   :members:
   :undoc-members:
