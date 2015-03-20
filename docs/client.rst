.. py:module:: aioconsul
.. _client:

Client
======

::

    from aioconsul import Consul
    client = Consul('my.node.ip', token='my.token', consistency='stale')


Internals
---------

.. autoclass:: aioconsul.Consul
   :members:
   :inherited-members:
