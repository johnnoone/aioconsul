from aioconsul.common import Response
from collections import namedtuple
from enum import Enum
from functools import singledispatch
import json


ConsulValue = namedtuple('namedtuple', 'value meta')
Blocking = namedtuple('Blocking', 'index wait')


class Consistency(Enum):
    default = "default"
    stale = "stale"
    consistent = "consistent"


@singledispatch
def consul(obj, meta=None):
    meta = meta or {}
    return ConsulValue(obj, meta=meta)


@consul.register(Response)
def consul_response(obj, meta=None):
    meta = meta or {}
    for k, v in extract_meta(obj.headers).items():
        meta.setdefault(k, v)
    return ConsulValue(obj.body, meta=meta)


def extract_meta(headers):
    meta = {}
    for k, v in headers.items():
        if k.lower().startswith("x-consul-"):
            k = k[9:]
            k = {
                'index': 'Index',
                'knownleader': 'KnownLeader',
                'lastcontact': 'LastContact',
                'token': 'Token',
                'translate-addresses': 'Translate-Addresses',
            }.get(k.lower(), k)
            meta[k] = json.loads(v)
    return meta
