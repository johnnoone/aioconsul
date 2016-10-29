import pytest


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.agent) == "<AgentEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_info(client):
    result = await client.agent.info()
    assert isinstance(result, dict)
    assert result["Config"]["ClientAddr"] == "127.0.0.1"
    assert result["Config"]["Datacenter"] == "dc1"
    assert result["Member"]["Addr"] == "127.0.0.1"


@pytest.mark.asyncio
async def test_maintenance(client, server):
    result = await client.agent.disable("testing")
    assert result is True
    result = await client.agent.enable("testing")
    assert result is True
