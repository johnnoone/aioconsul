import pytest
from aioconsul import Consul
from collections.abc import Mapping, Sequence


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.coordinate) == "<CoordinateEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_datacenters(client, server):
    datacenters = await client.coordinate.datacenters()
    assert isinstance(datacenters, Mapping)
    assert server.dc in datacenters
    assert datacenters[server.dc]["Datacenter"] == server.dc
    assert datacenters[server.dc]["Coordinates"][0]["Node"] == server.name


@pytest.mark.asyncio
async def test_nodes(client):
    nodes, meta = await client.coordinate.nodes(dc="dc1")
    assert isinstance(nodes, Sequence)
    assert "Index" in meta
    assert "KnownLeader" in meta
    assert "LastContact" in meta
