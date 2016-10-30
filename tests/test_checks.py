import pytest
from datetime import timedelta


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.checks) == "<ChecksEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_no_checks(client):
    result = await client.checks.items()
    assert isinstance(result, dict)
    assert not result


@pytest.mark.asyncio
async def test_check_ttl(client, server):
    check = {
        "ID": "foobar",
        "Name": "Foobar bar check",
        "TTL": timedelta(seconds=2),
    }
    result = await client.checks.register(check)
    assert result is True

    result = await client.checks.items()
    assert isinstance(result, dict)
    assert "foobar" in result
    assert result["foobar"]["Status"] == "critical"

    # TODO check in catalog that is really critical

    result = await client.checks.passing(check)
    assert result is True

    result = await client.checks.items()
    assert isinstance(result, dict)
    assert "foobar" in result
    assert result["foobar"]["Status"] == "passing"

    # TODO check in catalog that is really passing

    result = await client.checks.warning(check)
    assert result is True

    result = await client.checks.items()
    assert isinstance(result, dict)
    assert "foobar" in result
    assert result["foobar"]["Status"] == "warning"

    # TODO check in catalog that is really warning

    result = await client.checks.critical(check)
    assert result is True

    result = await client.checks.items()
    assert isinstance(result, dict)
    assert "foobar" in result
    assert result["foobar"]["Status"] == "critical"

    # TODO check in catalog that is really critical

    result = await client.checks.deregister(check)
    assert result is True

    result = await client.checks.items()
    assert isinstance(result, dict)
    assert "foobar" not in result
