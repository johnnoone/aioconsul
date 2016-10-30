import pytest
from json import dumps
from aioconsul.encoders import json
from datetime import datetime, timedelta


@pytest.mark.parametrize("input, expected", [
    (timedelta(seconds=10), "10s"),
    (datetime(2016, 12, 11), "2016-12-11T00:00:00"),
    ("foo", "foo"),
], ids=["duration", "datetime", "string"])
def test_json(input, expected):
    assert json.dumps(input) == dumps(expected)
