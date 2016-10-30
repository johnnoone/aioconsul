import pytest
from collections.abc import Mapping, Sequence


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.event) == "<EventEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_event(client):
    event = await client.event.fire("foobar")
    assert isinstance(event, Mapping)
    assert "Name" in event
    assert "NodeFilter" in event
    assert "TagFilter" in event
    assert "ID" in event
    assert "Payload" in event
    assert "ServiceFilter" in event
    assert "Version" in event
    assert "LTime" in event

    items, meta = await client.event.items("foobar")
    assert isinstance(items, Sequence)
    assert "Index" in meta
    assert "KnownLeader" not in meta
    assert "LastIndex" not in meta


@pytest.mark.asyncio
async def test_payload(client):
    event = await client.event.fire("bazqux", payload=b"foobar")
    assert event["Name"] == "bazqux"
    assert event["Payload"] == b"foobar"

    items, _ = await client.event.items("bazqux")
    for elt in items:
        if elt["ID"] == event["ID"]:
            break
    else:
        pytest.fail("Unable to find event")
    assert elt["ID"] == event["ID"]
    assert elt["Name"] == event["Name"]
    assert elt["Payload"] == event["Payload"]
