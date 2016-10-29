import asyncio
import pytest
from aioconsul import Consul, UnauthorizedError, NotFound
from aioconsul.typing import Hidden


@pytest.mark.asyncio
async def test_kv(client, server):
    await client.kv.set("foo", b"bar")
    await client.kv.set("foo/bar", b"bar")

    token = await client.acl.create({
        "Name": "foo-acl",
        "Rules": """
            key "" { policy = "read" }
            key "foo/" { policy = "deny" }
        """
    })

    await asyncio.sleep(1)
    tokens, _ = await client.acl.items()

    # anonymous permission
    node = Consul(server.address)
    await node.acl.info(token)
    with pytest.raises(UnauthorizedError):
        await node.acl.items()
    with pytest.raises(NotFound):
        await node.kv.get("foo")
    with pytest.raises(UnauthorizedError):
        await node.kv.set("foo", b"baz")

    # constrained permission
    node.token = token
    await node.acl.info(token)
    with pytest.raises(UnauthorizedError):
        await node.acl.items()
    await node.kv.get("foo")
    with pytest.raises(UnauthorizedError):
        await node.kv.set("foo", b"baz")
    with pytest.raises(NotFound):
        await node.kv.get("foo/bar")

    # do the clean
    response = await client.acl.destroy(token)
    assert response

    with pytest.raises(NotFound):
        await node.acl.info(token)

    with pytest.raises(NotFound):
        await client.acl.info(token)


@pytest.mark.asyncio
async def test_query(client, server):
    token = await client.acl.create({
        "Name": "foo-acl",
        "Rules": """
            query "bar" { policy = "read" }
        """
    })

    node = Consul(server.address)
    res = await node.query.items()
    assert not res

    res = await client.query.items()
    assert not res

    with pytest.raises(UnauthorizedError):
        await node.query.create({
            "Name": "my-query",
            "Service": {
                "Service": "redis"
            }
        })

    await client.query.create({
        "Name": "foo-query",
        "Token": "token-query",
        "Service": {
            "Service": "redis"
        }
    })

    await client.query.create({
        "Name": "bar-query",
        "Token": "token-query",
        "Service": {
            "Service": "redis"
        }
    })

    res = await client.query.items()
    assert len(res) == 2
    assert res[0]["Token"] == "token-query"
    assert res[1]["Token"] == "token-query"

    res = await node.query.items()
    assert not res

    node.token = token
    res = await node.query.items()
    assert len(res) == 1
    assert res[0]["Token"] is Hidden
