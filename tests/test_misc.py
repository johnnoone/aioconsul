from aioconsul import codec


def test_decode():
    obj1 = codec.ConsulString('toto',
                              consul=codec.ConsulMeta(1, 2, 3, 4))
    assert obj1 == 'toto'
    assert obj1.consul.key == 1

    
    obj2 = codec.decode({
        'Key': 1,
        'Value': 'toto'
    }, base64=False)

    assert obj2 == 'toto'
    assert obj2.consul.key == 1


def test_encode_string():
    src = 'foo'
    obj = codec.encode(src)
    assert obj == {'Flags': 1, 'Value': 'foo'}

    obj = codec.encode(src, lock_index='quux')
    assert obj == {'Flags': 1, 'Value': 'foo', 'LockIndex': 'quux'}

    src = codec.ConsulString('bar', consul=codec.ConsulMeta(1, 2, 3, 4))
    obj = codec.encode(src)
    assert obj == {'Flags': 1, 'Value': 'bar',
                    'Key': 1, 'CreateIndex': 2,
                    'LockIndex': 3, 'ModifyIndex': 4}
    obj = codec.encode(src, lock_index='quux')
    assert obj == {'Flags': 1, 'Value': 'bar',
                   'Key': 1, 'CreateIndex': 2,
                   'LockIndex': 'quux', 'ModifyIndex': 4}
