
AIOConsul
=========

AIOConsul is a Python >= 3.5 library for requesting Consul_ API, build on top
of asyncio_ and aiohttp_.

Currently, this library aims a full compatibility with consul 0.7.

Sources are available at https://lab.errorist.xyz/aio/aioconsul.

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
    members = await client.members.items()
    assert len(members) == 1, "I am alone in my cluster"

    # let's join another cluster
    joined = await client.members.join('other.node.ip')
    if joined:
        members = await client.members.items()
        assert len(members) > 1, "I'm not alone anymore"

And display the catalog::

    datacenters = await client.catalog.datacenters()
    for dc in datacenters:
        print(dc)

    services, _ = await client.catalog.services()
    for service, tags in services.items():
        print(service, tags)

    nodes, _ = await client.catalog.nodes()
    for node in nodes:
        print(node.name, node.address)


Important
---------

Version 0.7 breaks compatibility with previous versions:

* It is closer to what HTTP API returns
* It does not add consul property anymore
* Response with metadata are now a 2 items length tuple
  (:class:`~aioconsul.typing.CollectionMeta` or
  :class:`~aioconsul.typing.ObjectMeta`)


Focus
-----

.. toctree::
   :maxdepth: 2

   client
   api
   endpoints
   misc
   contributing

.. _Consul: https://www.consul.io
.. _asyncio: http://asyncio.org
.. _aiohttp: http://aiohttp.readthedocs.org
