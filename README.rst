AIO Consul
----------

Consul_ has multiple components, but as a whole, it is a tool for discovering and configuring services in your infrastructure, like :

* Service Discovery
* Health Checking
* Key/Value Store
* Multi Datacenter


This library provides several features to interact with its API. It is build in top of asyncio_ and aiohttp_. It works with Python >= 3.3, and is still a work in progress.

The documentation_ has more details, but sparsely this is how to work with it.

Installation
~~~~~~~~~~~~

::

    pip install aioconsul


Usage
~~~~~

Most of the functions are coroutines, so it must be embedded into asyncio tasks::

    from aioconsul import Consul
    client = Consul()

    @asyncio.coroutine
    def main():
        node_name = yield from client.agent.config().node_name
        print('I am %s!' % node_name)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main)
    loop.run_until_complete(future)


Agent checks
~~~~~~~~~~~~

Currently this library can handle simple checks::

    from aioconsul import Consul
    client = Consul()

    # list all checks
    for check in (yield from client.agent.checks.items()):
        print(check.id)

    # look for a check
    check = yield from client.agent.checks.get('my-check')

    # register a script check
    check = yield from client.agent.checks.register_script('my-script-check',
                                                           script='~/script.sh',
                                                           interval='5m')

    # register a http check
    check = yield from client.agent.checks.register_ttl('my-http-check',
                                                        http='http://example.com',
                                                        interval='10h')

    # register a ttl check
    check = yield from client.agent.checks.register_ttl('my-ttl-check',
                                                        ttl='10s')

    # mark ttl check passing
    yield from client.agent.checks.passing(check, note='Make it so')

    # deregister any check
    yield from client.agent.checks.deregister(check)


Agent services
~~~~~~~~~~~~~~

Currently this library can handle simple checks::

    from aioconsul import Consul
    client = Consul()

    # list all services
    for srv in (yield from client.agent.services.items()):
        print(srv.id)

    # search a service by its name
    srv = yield from client.agent.services.get('my-service')

    # disable a service
    yield from client.agent.services.maintenance(srv,
                                                 enable=False,
                                                 reason='Migrating stuff')

    # and reenable it
    yield from client.agent.services.maintenance(srv,
                                                 enable=True,
                                                 reason='Done')


Catalog
~~~~~~~

This library can consult catalog::

    from aioconsul import Consul
    client = Consul()

    # listing all nodes from catalog
    for node in (yield from client.catalog.nodes()):
        print(node.name)
        print(node.address)

    # getting a node with all of its service
    node = yield from client.catalog.get('my-node')
    print(node.services)

    # getting all nodes that belong to a service
    nodes = yield from client.catalog.nodes(service='my-service')
    print(nodes)

And register checks, services and nodes::

    from aioconsul import Consul
    client = Consul()

    node = {'name': 'my-local-node',
            'address': '127.0.0.1'}
    check = {'name': 'baz',
             'state': 'passing',
             'service_id': 'bar'}
    service={'name': 'bar'}

    resp = yield from client.catalog.register(node, check=check, service=service)
    assert resp

    resp = yield from client.catalog.deregister(node, check=check, service=service)
    assert resp


Events
~~~~~~

::

    from aioconsul import Consul
    client = Consul()

    # send an event
    event = yield from client.event.fire('my-event', node_filter='.*')

    # list all events
    for event in (yield from client.event.items()):
        print(event.name)


Health
~~~~~~

::

    from aioconsul import Consul
    client = Consul()

    # checks for a node
    for check in (yield from client.health.node('my-local-node')):
        assert check.status == 'passing'

    # health of a node
    for check in (yield from client.health.node('my-local-node')):
        assert check.status == 'passing'

    # health of a check id
    for check in (yield from client.health.checks('serfHealth')):
        assert check.status == 'passing'

    # health of a check id
    for check in (yield from client.health.checks('serfHealth')):
        assert check.status == 'passing'

    # health of a service
    for node in (yield from client.health.service('foo', state='any')):
        for check in node.checks:
            if check.id == 'service:foo':
                assert check.status == 'passing'

    # passing checks
    for check in (yield from client.health.state('passing')):
        assert check.status == 'passing'


KV and Sessions
~~~~~~~~~~~~~~~

Simple example::

    from aioconsul import Consul
    client = Consul()

    # set a k/v
    yield from client.kv.set('my.key', 'my.value')

    # fetch a k/v
    obj = yield from client.kv.get('my.key')

    # fetched values have a special attribute `consul`
    assert obj.key.name == 'my.key'

    # delete a k/v
    yield from client.kv.delete('my.key')


Many k/v::

    # list many k/v
    for key, value in (yield from client.kv.items('')):
        print(key, value)


Ephemeral k/v::

    session = yield from client.session.create(behavior='delete')
    yield from client.kv.create('my.key', 'my.key')
    yield from client.session.delete(session)

    try:
        # try to fetch previous k/v
        obj = yield from client.kv.get('my.key')
    except client.kv.NotFound:
        # but it was destroyed with the session
        pass


ACL
~~~

::

    from aioconsul import Consul, ACLPermissionDenied
    client = Consul(token=master_token)

    # create a token
    token = (yield from client.acl.create('my-acl', rules=[
        ('key', '', 'read'),
        ('key', 'foo/', 'deny'),
    ]))

    # access to kv with the fresh token
    node = Consul(token=token)
    yield from node.kv.get('foo')
    with pytest.raises(ACLPermissionDenied):
        yield from node.kv.set('foo', 'baz')
    with pytest.raises(node.kv.NotFound):
        yield from node.kv.get('foo/bar')


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
.. _documentation: http://aioconsul.readthedocs.org
