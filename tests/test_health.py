import pytest
from collections.abc import Sequence


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.health) == "<HealthEndpoint(%r)>" % str(client.address)


@pytest.mark.parametrize("node", [
    "server1", {"Node": "server1"}, {"ID": "server1"}
])
@pytest.mark.asyncio
async def test_node(client, node):
    data, meta = await client.health.node(node)
    assert isinstance(data, Sequence)
    assert data[0]["Node"] == "server1"
    assert_meta(meta)


@pytest.mark.parametrize("service", [
    "redis", {"ServiceID": "redis"}, {"ID": "redis"}
])
@pytest.mark.asyncio
async def test_checks(client, service):
    data, meta = await client.health.checks(service)
    assert isinstance(data, Sequence)
    assert_meta(meta)


@pytest.mark.parametrize("service", [
    "redis", {"ServiceID": "redis"}, {"ID": "redis"}
])
@pytest.mark.asyncio
async def test_service(client, service):
    data, meta = await client.health.service(service)
    assert isinstance(data, Sequence)
    assert_meta(meta)


@pytest.mark.parametrize("state", [
    "any", "passing", "warning", "critical"
])
@pytest.mark.asyncio
async def test_state(client, state):
    data, meta = await client.health.state(state)
    assert isinstance(data, Sequence)
    assert_meta(meta)


def assert_meta(data):
    assert "Index" in data
    assert "KnownLeader" in data
    assert "LastContact" in data
