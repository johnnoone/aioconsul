import pytest
import re
from aioconsul.util import extract_attr, extract_pattern


@pytest.mark.parametrize("input, keys, output", [
    (1, ["foo"], 1),
    ({"foo": 1}, ["foo"], 1)
])
def test_extract(input, keys, output):
    assert extract_attr(input, keys=keys) == output


@pytest.mark.parametrize("input, keys", [
    ({"foo": 1}, ["bar"]),
])
def test_extract_error(input, keys):
    with pytest.raises(TypeError):
        extract_attr(input, keys=keys)


@pytest.mark.parametrize("input, output", [
    ("foo", "foo"),
    (re.compile("foo"), "foo")
])
def test_extract_pattern(input, output):
    assert extract_pattern(input) == output
