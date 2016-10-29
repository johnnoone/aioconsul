import pytest
from collections.abc import Mapping, Sequence


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.catalog) == "<CatalogEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_datacenters(client, server):
    data = await client.catalog.datacenters()
    assert isinstance(data, Sequence)
    assert server.dc in data


@pytest.mark.asyncio
async def test_nodes(client, server):
    data, meta = await client.catalog.nodes()
    assert isinstance(data, Sequence)
    assert extract_node(data, server.name, "127.0.0.1")
    assert "Index" in meta
    assert "KnownLeader" in meta
    assert "LastContact" in meta


@pytest.mark.asyncio
async def test_services(client):
    data, meta = await client.catalog.services()
    assert isinstance(data, Mapping)
    assert data == {"consul": []}
    assert "Index" in meta
    assert "KnownLeader" in meta
    assert "LastContact" in meta


@pytest.mark.asyncio
async def test_register_node(client):
    data = await client.catalog.register_node({
        "Node": "google1",
        "Address": "google.com"
    })
    assert data is True

    data, _ = await client.catalog.nodes()
    assert extract_node(data, "google1", "google.com")

    data = await client.catalog.deregister_node({
        "Node": "google1"
    })
    assert data is True

    data, _ = await client.catalog.nodes()
    assert not extract_node(data, "google1", "google.com")


@pytest.mark.asyncio
async def test_register_service(client):
    data = await client.catalog.register_service({
        "Node": "google1",
        "Address": "google.com"
    }, service={
        "ID": "redis1",
        "Service": "redis"
    })
    assert data is True

    data, _ = await client.catalog.services()
    assert "redis" in data

    data = await client.catalog.deregister_service("google1", service="redis1")
    assert data is True

    data, _ = await client.catalog.services()
    assert "redis" not in data


@pytest.mark.asyncio
async def test_register_check(client):
    data = await client.catalog.register_check({
        "Node": "google1",
        "Address": "google.com"
    }, check={
        "CheckID": "check1",
        "Name": "Redis health check",
        "Notes": "Script based health check",
        "Status": "passing"
    })
    assert data is True

    data = await client.catalog.deregister_check("google1", check="check1")
    assert data is True


@pytest.mark.asyncio
async def test_service(client):
    nodes, meta = await client.catalog.service("foo")
    assert isinstance(nodes, Sequence)
    assert not nodes


@pytest.mark.asyncio
async def test_node(client):
    node, meta = await client.catalog.node("foo")
    assert node is None


def extract_node(data, name, address):
    for d in data:
        if d["Address"] == address and d["Node"] == name:
            return d
