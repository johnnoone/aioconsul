from collections import namedtuple
from collections.abc import Mapping


Response = namedtuple("Response", "url status body headers method")


class Response:

    def __init__(self, url, status, body, headers, method):
        self.url = url
        self.status = status
        self.body = body
        self.headers = headers
        self.method = method

    def __repr__(self):
        return "<%s(method=%r, url=%r, status=%r, body=%r, headers=%r)>" % (
            self.__class__.__name__,
            self.method,
            self.url,
            self.status,
            self.body,
            self.headers
        )


def extract_body(obj):
    if isinstance(obj, Response):
        return obj.body
    return obj


def extract_id(obj, keys=None):
    obj = extract_body(obj)
    if isinstance(obj, Mapping):
        keys = keys or ["ID"]
        for key in keys:
            if key in obj:
                return obj[key]
        raise KeyError("id not found in object")
    return getattr(obj, "id", obj)


def extract_address(obj, keys=None):
    obj = extract_body(obj)
    if isinstance(obj, Mapping):
        keys = keys or ["Address"]
        for key in keys:
            if key in obj:
                return obj[key]
        raise KeyError("address not found in object")
    return getattr(obj, "address", obj)


def decode_watch(watch):
    index, wait = None, None
    if isinstance(watch, tuple):
        index, wait = watch
    else:
        index, wait = watch, None
    return extract_index(index), wait


def extract_index(obj, keys=None):
    if isinstance(obj, Mapping):
        keys = keys or ["ModifyIndex", "Index"]
        for key in keys:
            if key in obj:
                return obj[key]
        raise KeyError("id not found in object")
    return obj
