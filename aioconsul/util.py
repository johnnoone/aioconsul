import asyncio
import inspect
from datetime import timedelta
from functools import partial, wraps

__all__ = ['extract_id', 'extract_name', 'extract_ref',
           'format_duration', 'task']


def extract_id(obj):
    """Extracts id from obj, if any"""
    return getattr(obj, 'id', obj)


def extract_name(obj):
    """Extracts name from obj, if any"""
    return getattr(obj, 'name', obj)


def extract_ref(obj):
    """Extracts ref from obj, if any.

    ref can be modify_index or last_index.
    """
    obj = getattr(obj, 'modify_index', obj)
    obj = getattr(obj, 'last_index', obj)
    return obj


def format_duration(obj):
    """Converts obj to consul duration"""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, int):
        return '%ss' % obj
    if isinstance(obj, timedelta):
        return '%ss' % int(obj.total_seconds())
    raise ValueError('wrong type %r' % obj)


def task(func=None, *, loop=None):
    """Transforms func into an asyncio task."""

    if not func:
        if not loop:
            raise ValueError('loop is required')
        return partial(task, loop=loop)

    if getattr(func, '_is_task', False):
        return func

    coro = asyncio.coroutine(func)

    if inspect.ismethod(func):
        @wraps(func)
        def wrapper(self, *arg, **kwargs):
            l = loop or self.loop
            return asyncio.async(coro(self, *arg, **kwargs), loop=l)
    else:
        @wraps(func)
        def wrapper(*arg, **kwargs):
            return asyncio.async(coro(*arg, **kwargs), loop=loop)
    wrapper._is_task = True
    return wrapper
