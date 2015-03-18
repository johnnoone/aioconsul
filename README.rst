AIO Consul
----------

Implements consul with asyncio.
It is not ready for production yet.
It works with python >= 3.3.


Installation
~~~~~~~~~~~~

::

    pip install aioconsul


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


Testing
~~~~~~~

1. Install consul, and then run it in a shell::

    consul agent -config-file=tests/consul-agent.json


2. In another console, run tests::

    py.test --cov-report html --cov aioconsul tests
