.. py:module:: aioconsul
.. _acl:

ACL
===

The ACL endpoints are used to create, update, destroy, and query ACL tokens.

How to create a new token:

.. code-block:: python

    from aioconsul import Consul, ACLPermissionDenied
    import pytest

    master = Consul(token='master.token')

    # create a token that disable almost everything
    token = (yield from master.acl.create('my-acl', rules=[
        ('key', '', 'read'),
        ('key', 'foo/', 'deny'),
    ]))

    # open a new master with the fresh token
    node = Consul(token=token)
    yield from node.kv.get('foo')

    # writes must be disabled
    with pytest.raises(ACLPermissionDenied):
        yield from node.kv.set('foo', 'baz')

    # everything under `foo/` must be hidden
    with pytest.raises(node.kv.NotFound):
        yield from node.kv.get('foo/bar')


How to list tokens:

.. code-block:: python

    from aioconsul import Consul
    master = Consul(token='master.token')

    # create a token that disable almost everything
    for token in (yield from master.acl():
        print(token)


See :class:`Token` and :class:`Rule`.


Internals
---------

.. autoclass:: aioconsul.ACLEndpoint
   :members:
   :undoc-members:
