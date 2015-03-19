from aioconsul import Consul
from conftest import async_test


@async_test
def test_support():
    client = Consul()

    assert client.acl.supported is None, 'Should be unknown at this time'
    response = yield from client.acl.is_supported()
    assert isinstance(response, bool)
    assert response == client.acl.supported


def test_leader(leader):
    assert 'acl_master_token' in leader, 'Cannot perform the running tests'
