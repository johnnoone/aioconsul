import pytest
from aioconsul import Consul


@pytest.mark.asyncio
async def test_client(server):
    client = Consul(server.address)
    assert str(client.address) == server.address
    assert repr(client) == "<Consul(%r)>" % server.address
