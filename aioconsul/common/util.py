import re
from datetime import timedelta


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
