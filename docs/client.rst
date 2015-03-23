.. py:module:: aioconsul
.. _client:

Client
======

::

    from aioconsul import Consul
    client = Consul('my.node.ip', token='my.token', consistency='stale')
    info = yield from client.agent.info()


Internals
---------

.. autoclass:: aioconsul.Consul
   :members:
   :inherited-members:
