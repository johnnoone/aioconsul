AIO Consul
----------

.. image:: https://lab.errorist.xyz/aio/aioconsul/badges/master/build.svg
   :target: https://lab.errorist.xyz/aio/aioconsul/commits/master

.. image:: https://lab.errorist.xyz/aio/aioconsul/badges/master/coverage.svg
  :target: https://lab.errorist.xyz/aio/aioconsul/commits/master


Consul_ has multiple components, but as a whole, it is a tool for discovering
and configuring services in your infrastructure, like:

* Service Discovery
* Health Checking
* Key/Value Store
* Multi Datacenter


This library provides several features to interact with its API. It is build
in top of asyncio_ and aiohttp_. It works with Python >= 3.5, and is still a
work in progress.

The documentation_ has more details, but sparsely this is how to work with it.

Installation
~~~~~~~~~~~~

::

    pip install aioconsul


Usage
~~~~~

Most of the functions are coroutines, so it must be embedded into asyncio
tasks::

    from aioconsul import Consul
    client = Consul()

    async def main():
        node = await client.agent.info()
        print('I am %s!' % node["Name"])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main)
    loop.run_until_complete(future)


Agent checks
~~~~~~~~~~~~

Currently this library can handle simple checks::

    from aioconsul import Consul
    client = Consul()

    # list all checks
    checks = await client.checks.items()
    for check in checks:
        print(check["ID"])

    # register a script check
    registered = await client.checks.register({
      "Name": "my-script-check",
      "Script": "~/script.sh",
      "Interval": "5m"})

    # register a http check
    registered = await client.checks.register({
      "Name": 'my-http-check',
      "HTTP": 'http://example.com',
      "Interval": '10h'})

    # register a ttl check
    registered = await client.checks.register({
      "Name": 'my-ttl-check',
      "ttl": '10s'})

    # mark ttl check passing
    await client.checks.passing('my-ttl-check', note='Make it so')

    # deregister any check
    await client.checks.deregister('my-ttl-check')


Agent services
~~~~~~~~~~~~~~

Currently this library can handle simple services::

    from aioconsul import Consul
    client = Consul()

    # list all services
    services = await client.services.items()
    for srv in services.value():
        print(srv["ID"])

    # disable a service
    await client.services.disable(srv, reason='Migrating stuff')

    # and reenable it
    await client.services.enable(srv, reason='Done')


Catalog
~~~~~~~

This library can consult catalog::

    from aioconsul import Consul
    client = Consul()

    # listing all nodes from catalog
    nodes, _ = await client.catalog.nodes()
    for node in nodes:
        print(node["Name"])
        print(node["Address"])

    # getting a node with all of its service
    node, _ = await client.catalog.node('my-node')
    print(node["Services"])

    # getting all nodes that belong to a service
    nodes, _ = await client.catalog.nodes(service='my-service')
    print(nodes)

And register checks, services and nodes::

    from aioconsul import Consul
    client = Consul()

    resp = await client.catalog.register({
      "Node": 'my-local-node',
      "Address": "127.0.0.1",
      "Check": {
        "Node": 'my-local-node',
        'Status': 'passing',
        "ServiceID": 'bar'
      },
      "Service": {'ID': 'bar'}
    })
    assert resp

    resp = await client.catalog.deregister({
      "Node": 'my-local-node'
    })
    assert resp


Events
~~~~~~

::

    from aioconsul import Consul
    client = Consul()

    # send an event
    event = await client.event.fire('my-event', node='.*')

    # list all events
    events, _ = await client.event.items()
    for event in events:
        print(event["Name"])


Health
~~~~~~

::

    from aioconsul import Consul
    client = Consul()

    # checks for a node
    checks, _ = await client.health.node('my-local-node')
    for check in checks:
        assert check["Status"] == 'passing'

    # health of a check id
    checks, _ = await client.health.checks('serfHealth')
    for check in checks:
        assert check["Status"] == 'passing'

    # health of a service
    checks, _ = await client.health.service('foo', state='any')
    for node in checks:
        for check in node["Checks"]:
            if check["ID"] == 'service:foo':
                assert check["Status"] == 'passing'

    # passing checks
    checks, _ = await client.health.state('passing')
    for check in checks:
        assert check["Status"] == 'passing'


KV and Sessions
~~~~~~~~~~~~~~~

Simple example::

    from aioconsul import Consul
    client = Consul()

    # set a k/v
    await client.kv.set('my.key', 'my.value')

    # fetch a k/v
    obj, _ = await client.kv.get('my.key')

    # fetched values have a special attribute `consul`
    assert obj['Key'] == 'my.key'

    # delete a k/v
    await client.kv.delete('my.key')


Many k/v::

    # list many k/v
    results, _ = await client.kv.get_tree('')
    async for obj in results:
        print(obj['Key'], obj['Value'])


Ephemeral k/v::

    session = await client.sessions.create({'Behavior': 'delete'})
    await client.kv.lock('my.key', 'my.key', session=session)
    await client.sessions.delete(session)

    try:
        # try to fetch previous k/v
        obj = await client.kv.get('my.key')
    except client.kv.NotFound:
        # but it was destroyed with the session
        pass


ACL
~~~

::

    from aioconsul import Consul, PermissionDenied
    client = Consul(token=master_token)

    # create a token
    token = await client.acl.create({
      'Name': 'my-acl',
      'Rules': [
        ('key', '', 'read'),
        ('key', 'foo/', 'deny'),
      ]
    })

    # access to kv with the fresh token
    node = Consul(token=token)
    await node.kv.get('foo')
    with pytest.raises(PermissionDenied):
        await node.kv.set('foo', 'baz')
    with pytest.raises(node.kv.NotFound):
        await node.kv.get('foo/bar')


Testing
~~~~~~~

Tests rely on Consul_ binary and `py.test`_.

1. Install consul binary, it must be reachable in your ``$PATH``.
2. Install test requirements::

    pip install -r requirements-tests.txt

3. Then run tests::

    py.test --cov-report html --cov aioconsul tests


Credits
-------

- Consul_
- aiohttp_
- asyncio_
- `py.test`_


.. _Consul: http://consul.io
.. _aiohttp: http://aiohttp.readthedocs.org
.. _asyncio: http://asyncio.org
.. _`py.test`: http://pytest.org
.. _documentation: http://aio.errorist.io/aioconsul
