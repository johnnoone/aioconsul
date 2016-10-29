import pytest
from aioconsul import Consul
from aioconsul.api import format_duration, extract_blocking
from datetime import timedelta


@pytest.mark.asyncio
async def test_client(server):
    client = Consul(server.address)
    assert str(client.address) == server.address
    assert repr(client) == "<Consul(%r)>" % server.address


@pytest.mark.parametrize("input, expected", [
    ("10s", "10s"),
    (None, None),
    (timedelta(seconds=10), "10s"),
])
@pytest.mark.asyncio
async def test_duration(input, expected):
    assert format_duration(input) == expected


@pytest.mark.parametrize("input, expected", [
    (10, (10, None)),
    ((10, 10), (10, 10)),
    ({"Index": 10}, (10, None)),
])
@pytest.mark.asyncio
async def test_blocking(input, expected):
    assert extract_blocking(input) == expected


@pytest.mark.parametrize("input", [
    ((1, 2, 3)),
])
@pytest.mark.asyncio
async def test_blocking_error(input):
    with pytest.raises(TypeError):
        extract_blocking(input)
