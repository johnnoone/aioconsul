import pytest
from aioconsul import Consul, NotFound
from collections.abc import Mapping, Sequence


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.kv) == "<KVEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_keys(client):
    with pytest.raises(NotFound):
        await client.kv.keys("foo")
    await client.kv.set("foo", bytes("bar", encoding="utf-8"))
    await client.kv.set("foo/bar", bytes("baz", encoding="utf-8"))
    result, meta = await client.kv.keys("foo")
    assert result == ["foo", "foo/bar"]
    assert "Index" in meta
    assert "KnownLeader" in meta
    assert "LastContact" in meta
    result = await client.kv.delete("foo")
    assert result is True
    result = await client.kv.delete("foo")
    assert result is True


@pytest.mark.asyncio
async def test_get(client):
    result = await client.kv.set("foo", bytes("bar", encoding="utf-8"))
    assert result is True
    result, meta = await client.kv.get("foo")
    assert "Index" in meta
    assert "KnownLeader" in meta
    assert "LastContact" in meta
    assert result["Value"] == bytes("bar", encoding="utf-8")
    result = await client.kv.delete("foo")
    assert result is True
    with pytest.raises(NotFound):
        await client.kv.get("foo")


@pytest.mark.asyncio
async def test_cas(client):
    result = await client.kv.set("foo", bytes("bar", encoding="utf-8"))
    assert result is True
    result, cas = await client.kv.get("foo")
    result = await client.kv.cas("foo", bytes("baz", encoding="utf-8"), index=999)
    assert result is False
    result = await client.kv.cas("foo", bytes("qux", encoding="utf-8"), index=cas)
    assert result is True
    result, cas = await client.kv.get("foo")
    assert result["Value"] == bytes("qux", encoding="utf-8")
    result = await client.kv.delete_cas("foo", index=999)
    assert result is False
    result, meta = await client.kv.get("foo")
    assert result["Value"] == bytes("qux", encoding="utf-8")
    result = await client.kv.delete_cas("foo", index=cas)
    assert result is True
    with pytest.raises(NotFound):
        await client.kv.get("foo")


@pytest.mark.asyncio
async def test_raw(client):
    result = await client.kv.set("foo", bytes("bar", encoding="utf-8"))
    assert result is True
    result, meta = await client.kv.raw("foo")
    assert result == bytes("bar", encoding="utf-8")
    assert "Index" in meta
    assert "KnownLeader" in meta
    assert "LastContact" in meta
    result = await client.kv.delete("foo")
    assert result is True
    with pytest.raises(NotFound):
        await client.kv.get("foo")


@pytest.mark.asyncio
async def test_transaction(client):
    tx = client.kv.prepare()
    tx.set("foo", b"bar")
    tx.get("foo")
    tx.delete("foo")
    ops = await tx.execute()
    assert isinstance(ops, Sequence)
    assert len(ops) == 2
    assert ops[0]["Key"] == "foo"
    assert ops[0]["Value"] is None
    assert ops[1]["Key"] == "foo"
    assert ops[1]["Value"] == b"bar"
