import pytest


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.members) == "<MembersEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_members(client, server):
    result = await client.members.items()
    assert isinstance(result, list)
    assert result[0]["Addr"] == "127.0.0.1"
    assert result[0]["Name"] == server.name


@pytest.mark.asyncio
async def test_members_wan(client, server):
    result = await client.members.items(wan=True)
    assert isinstance(result, list)
    assert result[0]["Addr"] == "127.0.0.1"
    assert result[0]["Name"] == "%s.%s" % (server.name, server.dc)
