import json
from base64 import b64decode
from aioconsul.bases import KeyMeta
from collections import namedtuple


def decode(data, base64=True):
    meta = KeyMeta(
        key=data.get('Key', None),
        create_index=data.get('CreateIndex', None),
        lock_index=data.get('LockIndex', None),
        modify_index=data.get('ModifyIndex', None)
    )

    value = data['Value']
    if base64:
        value = b64decode(value).decode('utf-8')

    flags = data.get('Flags', 0)
    for ct in TYPES:
        if flags == ct.flags:
            break
    else:
        ct = DEFAULT_TYPE
    return ct.type(ct.decoder(value), consul=meta)


def encode(value, **params):
    response = {}
    if hasattr(value, 'consul'):
        meta = value.consul
        response.setdefault('Key', meta.key)
        response.setdefault('CreateIndex', meta.create_index)
        response.setdefault('LockIndex', meta.lock_index)
        response.setdefault('ModifyIndex', meta.modify_index)
    if 'key' in params:
        response['Key'] = params['key']
    if 'create_index' in params:
        response['CreateIndex'] = params['create_index']
    if 'lock_index' in params:
        response['LockIndex'] = params['lock_index']
    if 'modify_index' in params:
        response['ModifyIndex'] = params['modify_index']

    for ct in TYPES:
        if isinstance(value, ct.base):
            response['Flags'] = ct.flags
            response['Value'] = ct.encoder(value)
            break
    else:
        response['Value'] = str(value)

    return response


class ConsulString(str):

    def __new__(cls, *args, consul, **kwargs):
        return str.__new__(cls, *args, **kwargs)

    def __init__(self, *args, consul, **kwargs):
        self.consul = consul


class ConsulInt(int):

    def __new__(cls, *args, consul, **kwargs):
        return str.__new__(cls, *args, **kwargs)

    def __init__(self, *args, consul, **kwargs):
        self.consul = consul


class ConsulSequence(list):

    def __new__(cls, *args, consul, **kwargs):
        return str.__new__(cls, *args, **kwargs)

    def __init__(self, *args, consul, **kwargs):
        self.consul = consul


class ConsulMapping(dict):

    def __new__(cls, *args, consul, **kwargs):
        return str.__new__(cls, *args, **kwargs)

    def __init__(self, *args, consul, **kwargs):
        self.consul = consul

ConsulType = namedtuple('ConsulType', 'flags type base decoder encoder')

TYPES = [
    ConsulType(1, ConsulString, str, lambda x: x, lambda x: x),
    ConsulType(2, ConsulInt, int, lambda x: x, lambda x: x),
    ConsulType(3, ConsulSequence, list, lambda x: x, lambda x: json.dumps(x)),
    ConsulType(4, ConsulMapping, dict, lambda x: x, lambda x: json.dumps(x))
]

# not necessarly a string
DEFAULT_TYPE = TYPES[0]
