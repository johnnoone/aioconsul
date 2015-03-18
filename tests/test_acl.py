import pytest
from aioconsul import Consul
from util import async_test


@async_test
def test_acl():
    client = Consul()

    assert client.acl.supported is None, 'Should be unknown at this time'
    response = yield from client.acl.is_supported()
    assert isinstance(response, bool)
    assert response == client.acl.supported
