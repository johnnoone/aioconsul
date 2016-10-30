import pytest
from aioconsul.client import util


@pytest.mark.parametrize("input, expected", [
    (None, (None, {})),
    ("foo", ("foo", {})),
    ({"ID": "foo"}, ("foo", {})),
    ({"Node": "foo"}, ("foo", {})),
    ({
        "Node": {
            "Node": "foobar",
            "Address": "10.1.10.12",
            "TaggedAddresses": {
                "lan": "10.1.10.12",
                "wan": "10.1.10.12"
            }
        },
        "Service": {},
        "Checks": []
    }, ("foobar", {
        "Node": "foobar",
        "Address": "10.1.10.12",
        "TaggedAddresses": {
            "lan": "10.1.10.12",
            "wan": "10.1.10.12"
        }
    })),
])
def test_prepare_node(input, expected):
    assert util.prepare_node(input) == expected


@pytest.mark.parametrize("input, expected", [
    (None, (None, {})),
    ("foo", ("foo", {})),
    ({"ID": "foo"}, ("foo", {})),
    ({
        "Node": {},
        "Service": {
            "ID": "redis1",
            "Service": "redis",
            "Tags": None,
            "Address": "10.1.10.12",
            "Port": 8000
        },
        "Checks": []
    }, ("redis1", {
        "ID": "redis1",
        "Service": "redis",
        "Tags": None,
        "Address": "10.1.10.12",
        "Port": 8000
    })),
    ({
        "Node": "foobar",
        "Address": "10.1.10.12",
        "ServiceID": "redis1",
        "ServiceName": "redis",
        "ServiceTags": None,
        "ServiceAddress": "",
        "ServicePort": 8000
    }, ("redis1", {
        "ID": "redis1",
        "Service": "redis",
        "Tags": None,
        "Address": "",
        "Port": 8000
    })),
    ({
        "ID": "redis1",
        "Name": "redis",
        "Tags": None,
        "Address": "",
        "Port": 8000
    }, ("redis1", {
        "ID": "redis1",
        "Service": "redis",
        "Tags": None,
        "Address": "",
        "Port": 8000
    }))
])
def test_prepare_service(input, expected):
    assert util.prepare_service(input) == expected


@pytest.mark.parametrize("input, expected", [
    (None, (None, {})),
    ("foo", ("foo", {})),
    ({"ID": "foo"}, ("foo", {})),
    ({"CheckID": "foo"}, ("foo", {})),
])
def test_prepare_check(input, expected):
    assert util.prepare_check(input) == expected
