import asyncio
import logging
import pytest
from aioconsul import Consul
from functools import wraps
from util import async_test

logger = logging.getLogger(__name__)


@async_test
def test_members():
    client = Consul()
    members = yield from client.agent.members()
    me = yield from client.agent.me()
    assert len(members) == 1
    assert me['Member'] == members[0]


@async_test
def test_maintenance():
    client = Consul()

    yield from client.agent.maintenance(True, 'Because!')
    checks = yield from client.agent.checks.items()
    print(checks)
    for check in checks:
        if check.status == 'critical':
            break
    else:
        assert False, "one check sould be at least critical"

    yield from client.agent.maintenance(False, 'Do you speak martien?')
    checks = yield from client.agent.checks.items()
    print(checks)
    for check in checks:
        assert check.status != 'critical'
