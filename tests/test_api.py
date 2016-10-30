import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("attr", [
    "stale", "consistent", "default", None
], ids=["stale", "consistent", "default", "unset"])
@pytest.mark.parametrize("consistency", [
    "stale", "consistent", "default", None
], ids=["stale", "consistent", "default", "unset"])
@pytest.mark.parametrize("params", [
    {"stale": True}, {"consistent": True}, {}
], ids=["stale", "consistent", "unset"])
async def test_consistency(client, attr, consistency, params):
    api = client.api
    api.consistency = attr
    await api.get("/v1/agent/self", consistency=consistency, params=params)
