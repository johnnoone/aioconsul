import pytest
from aioconsul.common import Address, parse_addr
from aioconsul.common import duration_to_timedelta, timedelta_to_duration
from datetime import timedelta


@pytest.mark.parametrize("a, b", [
    ("10s", timedelta(seconds=10)),
    ("2m", timedelta(minutes=2)),
    ("2h", timedelta(hours=2)),
    ("2d", timedelta(days=2)),
])
def test_duration(a, b):
    assert duration_to_timedelta(a) == b
    assert a == timedelta_to_duration(b)


@pytest.mark.parametrize("input, expected", [
    ("localhost",
     Address(proto=None, host="localhost", port=None)),
    ("http://localhost",
     Address(proto="http", host="localhost", port=None)),
    ("udp://localhost",
     Address(proto="udp", host="localhost", port=None)),
    ("tcp://localhost",
     Address(proto="tcp", host="localhost", port=None)),
    ("unix://localhost",
     Address(proto="unix", host="localhost", port=None)),
    (("localhost", 8080),
     Address(proto=None, host="localhost", port=8080)),
    (8080,
     Address(proto=None, host=None, port=8080)),
    ("127.0.0.1:8080",
     Address(proto=None, host="127.0.0.1", port=8080)),
    (Address(proto=None, host="localhost", port=None),
     Address(proto=None, host="localhost", port=None)),
])
def test_addr(input, expected):
    assert parse_addr(input) == expected
