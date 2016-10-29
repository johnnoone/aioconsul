import pytest


@pytest.mark.asyncio
async def test_endpoint(client):
    name = "<ServicesEndpoint(%r)>" % str(client.address)
    assert repr(client.services) == name


@pytest.mark.asyncio
async def test_services(client):
    result = await client.services.items()
    assert isinstance(result, dict)
    assert result["consul"]["ID"] == "consul"
    assert result["consul"]["Service"] == "consul"


@pytest.mark.asyncio
async def test_service(client):
    service = {
        "ID": "redis1",
        "Name": "redis",
        "Tags": [
            "master",
            "v1"
        ],
        "Address": "127.0.0.1",
        "Port": 8000,
        "Check": {
            "TTL": "15s"
        }
    }
    result = await client.services.register(service)
    assert result is True

    result = await client.services.items()
    assert isinstance(result, dict)
    assert result["redis1"]["ID"] == "redis1"
    assert result["redis1"]["Service"] == "redis"

    result = await client.checks.items()
    assert isinstance(result, dict)
    assert "service:redis1" in result
    assert result["service:redis1"]["CheckID"] == "service:redis1"
    assert result["service:redis1"]["Status"] == "critical"

    # TODO test warn, crit, pass of current ttl check

    result = await client.services.enable(service)
    assert result is True
    # TODO test it's remove from catalog

    result = await client.services.disable(service)
    assert result is True
    # TODO test it's into to catalog

    result = await client.services.deregister(service)
    assert result is True
