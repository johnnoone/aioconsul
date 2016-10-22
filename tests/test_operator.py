import pytest
from aioconsul import Consul


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.operator) == "<OperatorEndpoint(%r)>" % str(client.address)
