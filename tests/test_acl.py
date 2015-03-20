import pytest
from aioconsul import ACLPermissionDenied
from aioconsul import Consul
from conftest import async_test


@async_test
def test_no_support():
    client = Consul()

    assert client.acl.supported is None, 'Should be unknown at this time'
    response = yield from client.acl.is_supported()
    assert isinstance(response, bool)
    assert response == client.acl.supported
    assert client.acl.supported is False, 'Should no be ready for acl'


@async_test
def test_leader(leader):
    assert 'acl_master_token' in leader, 'Cannot perform the running tests'

    client = Consul(token=leader['acl_master_token'])

    assert client.acl.supported is None, 'Should be unknown at this time'
    response = yield from client.acl.is_supported()
    assert isinstance(response, bool)
    assert response == client.acl.supported
    assert client.acl.supported is True, 'Should be ready for acl'

    # remove acl
    acls = yield from client.acl.items()
    for acl in acls:
        if acl.name not in ('Master Token', 'Anonymous Token'):
            yield from client.acl.destroy(acl)

    wanted = {leader['acl_master_token'], 'anonymous'}
    found = {acl for acl in (yield from client.acl.items()) if acl.id in wanted}
    assert len(wanted) == len(found)

    token = yield from client.acl.create('foo-acl', rules=[
        ('key', '', 'deny'),
    ])

    acl = yield from client.acl.get(token)
    assert len(acl.rules) == 1
    for rule in acl:
        assert rule.type == 'key'
        assert rule.policy == 'deny'

    token = (yield from client.acl.update(token, name='foo-acl', rules=[
        ('key', '', 'read'),
        ('key', 'foo/', 'deny'),
    ]))

    for acl in (yield from client.acl.items()):
        if acl.name == 'foo-acl':
            assert acl.id == token
            break
    else:
        assert False, 'Token not found'

    acl = yield from client.acl.get(token)
    assert len(acl.rules) == 2
    for rule in acl:
        assert rule.type == 'key'
        assert rule.value in ('', 'foo/')

    yield from client.kv.set('foo', 'bar')
    yield from client.kv.set('foo/bar', 'bar')

    node = Consul()
    yield from node.kv.get('foo')
    yield from node.kv.set('foo', 'quux')
    yield from node.kv.get('foo/bar')

    node = Consul(token=token)
    yield from node.kv.get('foo')
    with pytest.raises(ACLPermissionDenied):
        yield from node.kv.set('foo', 'baz')
    with pytest.raises(node.kv.NotFound):
        yield from node.kv.get('foo/bar')

    # do the clean
    response = yield from client.acl.destroy(token)
    assert response

    with pytest.raises(client.acl.NotFound):
        yield from client.acl.get(token)
