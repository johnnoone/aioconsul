import pytest
from aioconsul import Consul


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.status) == "<StatusEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_leader(client):
    data = await client.status.leader()
    assert data == "127.0.0.1:8300"


@pytest.mark.asyncio
async def test_peers(client):
    data = await client.status.peers()
    assert data == set(["127.0.0.1:8300"])
