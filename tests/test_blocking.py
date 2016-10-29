import asyncio
import pytest
from collections.abc import Mapping, Sequence


@pytest.mark.asyncio
async def test_nodes(client, server, event_loop):
    _, meta = await client.catalog.nodes()
    watch1 = event_loop.create_task(client.catalog.nodes(watch=meta))
    watch2 = event_loop.create_task(client.catalog.node(server.name,
                                                        watch=meta))
    release = event_loop.create_task(client.catalog.register({
        "Node": "foobar",
        "Address": "192.168.10.10",
        "Service": {
            "ID": "foobar",
            "Service": "foobar",
        }
    }))

    await asyncio.wait([watch1, watch2, release], loop=event_loop, timeout=5)

    data, _ = watch1.result()
    assert isinstance(data, Sequence)
    assert data[0]["Address"] == "192.168.10.10"
    assert data[0]["Node"] == "foobar"
    assert data[1]["Address"] == "127.0.0.1"
    assert data[1]["Node"] == server.name

    data, _ = watch2.result()
    assert isinstance(data, Mapping)
    assert data["Node"]["Address"] == "127.0.0.1"
    assert data["Node"]["Node"] == server.name

    data = release.result()
    assert data is True


@pytest.mark.asyncio
async def test_services(client, event_loop):
    _, meta = await client.catalog.services()
    watch1 = event_loop.create_task(client.catalog.services(watch=meta))
    watch2 = event_loop.create_task(client.catalog.service("foobar",
                                                           watch=meta))
    release = event_loop.create_task(client.catalog.register({
        "Node": "foobar",
        "Address": "192.168.10.10",
        "Service": {
            "ID": "foobar",
            "Service": "foobar",
        }
    }))

    await asyncio.wait([watch1, watch2, release], loop=event_loop, timeout=5)

    data, _ = watch1.result()
    assert isinstance(data, Mapping)
    assert "foobar" in data

    data, _ = watch2.result()
    assert isinstance(data, Sequence)
    assert data[0]["Address"] == "192.168.10.10"
    assert data[0]["Node"] == "foobar"

    data = release.result()
    assert data is True
