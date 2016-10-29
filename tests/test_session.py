import pytest
from aioconsul import ConsulError, NotFound
from collections.abc import Mapping, Sequence


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.session) == "<SessionEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_bad_uuid(client):
    with pytest.raises(ConsulError):
        await client.session.info("foo")


@pytest.mark.asyncio
async def test_bad_format(client):
    session = "b318c74e-75a5-42e8-8f24-1065ba73f256"
    with pytest.raises(ConsulError):
        await client.session.create(session)


@pytest.mark.asyncio
async def test_empty(client):
    session = "b318c74e-75a5-42e8-8f24-1065ba73f256"

    with pytest.raises(NotFound):
        await client.session.info(session)

    result = await client.session.destroy(session)
    assert result is True


@pytest.mark.asyncio
async def test_create_bad_node(client):
    with pytest.raises(ConsulError):
        await client.session.create({
            "LockDelay": "15s",
            "Name": "my-service-lock",
            "Node": "foobar",
            "Checks": ["a", "b", "c"],
            "Behavior": "release",
            "TTL": "0s"
        })


@pytest.mark.asyncio
async def test_create_bad_check(client, server):
    with pytest.raises(ConsulError):
        await client.session.create({
            "LockDelay": "15s",
            "Name": "my-service-lock",
            "Node": server.name,
            "Checks": ["a", "b", "c"],
            "Behavior": "release",
            "TTL": "0s"
        })


@pytest.mark.asyncio
async def test_not_node(client, server):
    node, meta = await client.session.node("foobar")
    assert isinstance(node, Sequence)
    assert not node
    "Index" in meta
    "KnownLeader" in meta
    "LastContact" in meta


@pytest.mark.asyncio
async def test_create_ok(client, server):
    session = await client.session.create({})
    assert isinstance(session, Mapping)
    assert "ID" in session

    info, meta = await client.session.info(session)
    assert isinstance(info, Mapping)
    assert info["Node"] == server.name
    assert info["ID"] == session["ID"]
    "Index" in meta
    "KnownLeader" in meta
    "LastContact" in meta

    node, meta = await client.session.node(server.name)
    assert isinstance(node, Sequence)
    assert info == node[0]

    items, meta = await client.session.items()
    assert isinstance(items, Sequence)
    assert info == items[0]

    renew, meta = await client.session.renew(session)
    assert isinstance(renew, Mapping)
    assert renew["Node"] == server.name
    assert renew["ID"] == session["ID"]

    result = await client.session.destroy(session)
    assert result is True

    with pytest.raises(NotFound):
        await client.session.renew(session)

    with pytest.raises(NotFound):
        await client.session.info(session)

    node, meta = await client.session.node(server.name)
    assert not node

    sessions, meta = await client.session.items()
    assert not sessions


@pytest.mark.asyncio
async def test_kv(client):
    session = await client.session.create({})

    result = await client.kv.lock("foo", b"bar", session=session)
    assert result is True

    result = await client.kv.unlock("foo", b"bar", session=session)
    assert result is True

    result = await client.session.destroy(session)
    assert result is True


@pytest.mark.asyncio
async def test_kv_transaction(client):
    session = await client.session.create({})

    txn = client.kv.prepare()
    txn.lock("foo", b"bar", session=session)
    txn.check_session("foo", session=session)
    txn.unlock("foo", b"bar", session=session)
    ops = await txn.execute()
    assert isinstance(ops, Sequence)
    assert ops[0]["Key"] == "foo"
    assert ops[0]["Value"] is None

    result = await client.session.destroy(session)
    assert result is True
