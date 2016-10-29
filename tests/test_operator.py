import pytest


@pytest.mark.asyncio
async def test_endpoint(client):
    name = "<OperatorEndpoint(%r)>" % str(client.address)
    assert repr(client.operator) == name
