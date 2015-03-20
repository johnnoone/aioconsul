.. AIO Consul documentation master file, created by
   sphinx-quickstart on Thu Mar 19 15:44:47 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

AIOConsul
=========

AIOConsul is a Python >= 3.3 library for requesting consul_ API, build on top of asyncio_ and aiohttp_.

Currently, this library aims a full compatibility with consul 0.5.


Installation
------------

::

    pip install aioconsul


Tutorial
--------

In this example I will show you how to join my cluster with another::

    from aioconsul import Consul
    client = Consul('my.node.ip')

    # do I have a members?
    members = yield from client.agent.members()
    assert len(members) == 1, "I am alone in my cluster"

    # let's join another cluster
    joined = yield from client.agent.join('other.node.ip')
    if joined:
        members = yield from client.agent.members()
        assert len(members) > 1, "I'm not alone anymore"

And display the catalog::

    for dc in (yield from client.catalog.datacenters()):
        print(dc)

    for service, tags in (yield from client.catalog.services()).items():
        print(service, tags)

    for node in (yield from client.catalog.nodes()):
        print(node.name, node.address)


In the pit
----------

.. toctree::
   :maxdepth: 1

   client
   objects


Endpoints
---------

.. toctree::
   :glob:
   :maxdepth: 1

   endpoints/*


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _consul: https://www.consul.io
.. _asyncio: http://asyncio.org
.. _aiohttp: http://aiohttp.readthedocs.org
