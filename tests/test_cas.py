import pytest
from aioconsul import NotFound
from collections.abc import Sequence


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.kv) == "<KVEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_create_only(client):
    await cas(client, "foo", b"bar", 0, True)
    await present(client, "foo", b"bar")
    await cas(client, "foo", b"baz", 0, True)
    await present(client, "foo", b"bar")


@pytest.mark.asyncio
async def test_cas(client):
    await cas(client, "foo", b"bar", 0, True)
    data = await present(client, "foo", b"bar")
    await cas(client, "foo", b"baz", data, True)
    data = await present(client, "foo", b"baz")


@pytest.mark.asyncio
async def test_cas_setted(client):
    await cas(client, "foo", b"bar", 0, True)
    await present(client, "foo", b"bar")


@pytest.mark.asyncio
async def test_cas_absent(client):
    await cas(client, "foo", b"bar", 42, False)
    await absent(client, "foo")


@pytest.mark.asyncio
async def test_transaction(client, master_token):
    txn = client.kv.prepare()
    txn.cas("foo", b"bar", index=0)
    ops = await txn.execute()
    assert isinstance(ops, Sequence)
    assert ops[0]["Key"] == "foo"
    assert ops[0]["Value"] is None

    txn = client.kv.prepare()
    txn.check_index("foo", index=ops[0])
    ops = await txn.execute()
    assert isinstance(ops, Sequence)
    assert ops[0]["Key"] == "foo"
    assert ops[0]["Value"] is None

    txn = client.kv.prepare()
    txn.delete_cas("foo", index=ops[0])
    ops = await txn.execute()
    assert isinstance(ops, Sequence)
    assert not ops


async def cas(client, key, value, index, updated):
    updated = await client.kv.cas(key, value, index=index)
    assert updated is updated
    return updated


async def present(client, key, value):
    data, meta = await client.kv.get(key)
    assert data["Value"] == value
    return data


async def absent(client, key):
    with pytest.raises(NotFound):
        await client.kv.get(key)
