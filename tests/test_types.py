import aioconsul
import pytest


def test_string():
    value = aioconsul.ConsulString('foo')
    value.consul = 'bar'
    with pytest.raises(AttributeError):
        value.consulator = 'baz'
    assert value == 'foo'


def test_mapping():
    value = aioconsul.ConsulMapping(foo='bar')
    value.consul = 'bar'
    with pytest.raises(AttributeError):
        value.consulator = 'baz'
    assert value == {'foo': 'bar'}


def test_sequence():
    value = aioconsul.ConsulSet(['foo', 'bar', 'baz'])
    value.consul = 'bar'
    with pytest.raises(AttributeError):
        value.consulator = 'baz'
    assert value == {'foo', 'bar', 'baz'}
