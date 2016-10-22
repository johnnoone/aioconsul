import dateutil.parser
import json
import re
from collections.abc import Mapping, Sequence
from datetime import timedelta, datetime


class cached_property:

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def bool_to_int(v):
    if isinstance(v, bool):
        return int(v)
    return v


def drop_null(obj):
    if isinstance(obj, dict):
        return {k: drop_null(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [drop_null(elt) for elt in obj]
    return obj


class ConsulEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Mapping):
            return dict(obj)
        elif isinstance(obj, Sequence):
            return list(obj)
        elif isinstance(obj, datetime):
            # convert to RFC 3339
            return obj.stftime(r"%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(obj, timedelta):
            # convert to duration
            return timedelta_to_duration(obj)
        return json.JSONEncoder.default(self, obj)


class Hidden:
    """Hidden value.

    Mostly Tokens will be redacted and displayed as <hidden>
    unless a management token is used.
    """
    pass


class ConsulDecoder:

    timedelta_fields = ("TTL", "LockDelay", "DeregisterCriticalServiceAfter")
    datetime_fields = ("LastSuccess", "LastError")
    hidden_value_fields = ("Token",)

    def __call__(self, dct):
        for field in self.timedelta_fields:
            if field in dct:
                # convert to timedelta
                value = dct[field]
                if isinstance(value, int):  # it's in nanoseconds
                    dct[field] = timedelta(seconds=value / 1000000000)
                else:
                    dct[field] = duration_to_timedelta(value)
        for field in self.datetime_fields:
            if field in dct:
                # convert to datetime
                dct[field] = dateutil.parser.parse(dct[field])
        for field in self.hidden_value_fields:
            if dct.get(field) == "<hidden>":
                # mark hidden value
                dct[field] = Hidden
        return dct


def json_encode(obj):
    return json.dumps(obj, cls=ConsulEncoder)


def json_decode(obj):
    return json.loads(obj, object_hook=ConsulDecoder())


DURATION_PATTERN = re.compile(r"""((?P<weeks>\d+)w)?
                                  ((?P<days>\d+)d)?
                                  ((?P<hours>\d+)h)?
                                  ((?P<minutes>\d+)m)?
                                  ((?P<seconds>\d+)s)?""", re.X)


def duration_to_timedelta(obj):
    """Converts duration to timedelta

    >>> duration_to_timedelta("10m")
    >>> datetime.timedelta(0, 600)
    """
    matches = DURATION_PATTERN.search(obj)
    matches = matches.groupdict(default="0")
    matches = {k: int(v) for k, v in matches.items()}
    return timedelta(**matches)


def timedelta_to_duration(obj):
    """Converts timedelta to duration

    >>> timedelta_to_duration(datetime.timedelta(0, 600))
    >>> "10m"
    """
    minutes, hours, days = 0, 0, 0
    seconds = int(obj.total_seconds())
    if seconds > 59:
        minutes = seconds // 60
        seconds = seconds % 60
    if minutes > 59:
        hours = minutes // 60
        minutes = minutes % 60
    if hours > 23:
        days = hours // 24
        hours = hours % 24
    response = []
    if days:
        response.append('%sd' % days)
    if hours:
        response.append('%sh' % hours)
    if minutes:
        response.append('%sm' % minutes)
    if seconds or not response:
        response.append('%ss' % seconds)
    return "".join(response)
