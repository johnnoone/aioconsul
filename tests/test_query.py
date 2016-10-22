import pytest
from aioconsul import Consul, ConsulError


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.query) == "<QueryEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_create(client):
    items = await client.query.items()
    assert isinstance(items, list)
    assert not items

    query = await client.query.create({
        "Name": "my-query",
        "Token": "",
        "Near": "server1",
        "Service": {
            "Service": "redis",
            "Failover": {
                "NearestN": 3,
                "Datacenters": ["dc1", "dc2"]
            },
            "OnlyPassing": False,
            "Tags": ["master", "!experimental"]
        },
        "DNS": {
            "TTL": "10s"
        }
    })
    assert isinstance(query, dict)
    assert "ID" in query

    items = await client.query.items()
    assert isinstance(items, list)
    assert items[0]["ID"] == query["ID"]

    q2 = await client.query.read(query)
    assert query["ID"] == q2["ID"]

    q2.update({"DNS": {"TTL": "5s"}})
    result = await client.query.update(q2)
    assert result is True

    data = await client.query.execute(q2)
    assert "Datacenter" in data
    assert "DNS" in data
    assert "Failovers" in data
    assert "Index" in data
    assert "KnownLeader" in data
    assert "LastContact" in data
    assert "Nodes" in data
    assert "Service" in data

    data = await client.query.explain(q2)
    assert "Index" in data
    assert "KnownLeader" in data
    assert "LastContact" in data
    assert "Query" in data

    result = await client.query.delete(query)
    assert result is True

    with pytest.raises(ConsulError):
        await client.query.delete(query)
