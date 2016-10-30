import pytest
from aioconsul import NotFound
from collections.abc import Sequence


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.kv) == "<KVEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_tree(client):
    await client.kv.set("foo", bytes("bar", encoding="utf-8"))
    await client.kv.set("foo/bar", bytes("baz", encoding="utf-8"))
    result, meta = await client.kv.get_tree("foo")
    assert "Index" in meta
    assert "KnownLeader" in meta
    assert "LastContact" in meta
    assert result[0]["Value"] == bytes("bar", encoding="utf-8")
    assert result[1]["Value"] == bytes("baz", encoding="utf-8")
    result = await client.kv.delete_tree("foo")
    assert result is True
    with pytest.raises(NotFound):
        await client.kv.get_tree("foo")


@pytest.mark.asyncio
async def test_transaction(client):
    tx = client.kv.prepare()
    tx.set("foo", bytes("bar", encoding="utf-8"))
    tx.set("foo/bar", bytes("baz", encoding="utf-8"))
    tx.get_tree("foo")
    ops = await tx.execute()
    assert isinstance(ops, Sequence)
    assert ops[0]["Key"] == "foo"
    assert ops[0]["Value"] is None
    assert ops[1]["Key"] == "foo/bar"
    assert ops[1]["Value"] is None
    assert ops[2]["Key"] == "foo"
    assert ops[2]["Value"] == b"bar"
    assert ops[3]["Key"] == "foo/bar"
    assert ops[3]["Value"] == b"baz"

    tx = client.kv.prepare()
    tx.delete_tree("foo")
    ops = await tx.execute()
    assert isinstance(ops, Sequence)
    assert not ops
