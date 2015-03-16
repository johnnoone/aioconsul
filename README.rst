AIO Consul
----------

Implements consul with asyncio

Testing
~~~~~~~

1. Install consul, and then run it in a shell::

    consul agent -config-file=tests/consul-agent.json


2. In another console, run tests::

    py.test --cov-report html --cov aioconsul tests
