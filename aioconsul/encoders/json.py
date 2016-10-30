import json
from aioconsul.common import timedelta_to_duration
from aioconsul.common import duration_to_timedelta
from aioconsul.typing import Hidden
from collections.abc import Mapping, Sequence
from datetime import timedelta, datetime
from dateutil.parser import parse as str_to_datetime


class Registry:

    def __init__(self):
        self.encoders = {}
        self.decoders = {}

    def encode(self, obj, **kwargs):
        for hook in self.encoders.values():
            value = hook(obj, **kwargs)
            if value is not None:
                return value
        return obj, False

    def decode(self, dct, **kwargs):
        for hook in self.decoders.values():
            value = hook(dct, **kwargs)
            if isinstance(value, dict):
                value = dct
        return dct

    def register(self, hook):
        orig = hook
        if isinstance(hook, type):
            hook = hook()
        if hasattr(hook, 'encode'):
            self.encoders[orig] = hook.encode
        if hasattr(hook, 'decode'):
            self.decoders[orig] = hook.decode
        return orig


registry = Registry()
register = registry.register


@register
class MappingEncoder:

    def encode(self, obj):
        if isinstance(obj, Mapping):
            return dict(obj), True


@register
class SequenceEncoder:

    def encode(self, obj):
        if isinstance(obj, Sequence):
            return list(obj), True


@register
class RFC3339Encoder:

    fields = ("LastSuccess", "LastError")

    def encode(self, obj):
        # convert to RFC 3339
        if isinstance(obj, datetime):
            return obj.isoformat(), True

    def decode(self, dct):
        for field in self.fields:
            if field in dct:
                # convert to datetime
                dct[field] = str_to_datetime(dct[field])
        return dct


@register
class DurationEncoder:

    fields = ("TTL", "LockDelay", "DeregisterCriticalServiceAfter")

    def encode(self, obj):
        # convert to duration
        if isinstance(obj, timedelta):
            return timedelta_to_duration(obj), True

    def decode(self, dct):
        for field in self.fields:
            if field in dct:
                # convert to timedelta
                value = dct[field]
                if isinstance(value, int):  # it's in nanoseconds
                    dct[field] = timedelta(seconds=value / 1000000000)
                else:
                    dct[field] = duration_to_timedelta(value)
        return dct


@register
class HiddenEncoder:

    fields = ("Token",)

    def decode(self, dct):
        for field in self.fields:
            if dct.get(field) == "<hidden>":
                # mark hidden value
                dct[field] = Hidden
        return dct


class Encoder(json.JSONEncoder):

    def default(self, obj):
        value, encoded = registry.encode(obj)
        if encoded:
            return value
        return super(Encoder).default(obj)


def dumps(obj, **kwargs):
    kwargs.setdefault('cls', Encoder)
    return json.dumps(obj, **kwargs)


def loads(obj, **kwargs):
    kwargs.setdefault("object_hook", registry.decode)
    return json.loads(obj, **kwargs)
