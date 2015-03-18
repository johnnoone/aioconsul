import asyncio
from aioconsul import Consul
from functools import wraps


def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(pre_clean())
        loop.run_until_complete(future)
    return wrapper


@asyncio.coroutine
def pre_clean():
    client = Consul()

    # remove checks
    checks = yield from client.agent.checks.items()
    for check in checks:
        yield from client.agent.checks.delete(check)

    # remove services
    services = yield from client.agent.services.items()
    for service in services:
        if service.id != 'consul':
            yield from client.agent.services.delete(service)

    # remove keys
    for key in (yield from client.kv.keys('')):
        yield from client.kv.delete(key)

    # remove sessions
    sessions = yield from client.session.items()
    for session in sessions:
        yield from client.session.delete(session)
