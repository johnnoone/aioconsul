from aioconsul import Consul
from conftest import async_test


@async_test
def test_members():
    client = Consul()
    members = yield from client.agent.members()
    me = yield from client.agent.me()
    assert me in members


@async_test
def test_config(leader):
    client = Consul()
    config = yield from client.agent.config()
    assert leader['data_dir'] == config.data_dir
    assert leader['node_name'] == config.node_name
    assert leader['server'] == config.server


@async_test
def test_maintenance():
    client = Consul()

    yield from client.agent.maintenance(True, 'Because!')
    checks = yield from client.agent.checks.items()
    for check in checks:
        if check.status == 'critical':
            break
    else:
        assert False, "one check sould be at least critical"

    yield from client.agent.maintenance(False, 'Do you speak martien?')
    checks = yield from client.agent.checks.items()
    for check in checks:
        assert check.status != 'critical'
