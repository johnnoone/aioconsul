from datetime import timedelta


def extract_id(obj):
    """Extracts id from obj, if any"""
    return getattr(obj, 'id', obj)


def extract_ref(obj):
    """Extracts ref from obj, if any.

    ref can be modify_index or last_index.
    """
    obj = getattr(obj, 'modify_index', obj)
    obj = getattr(obj, 'last_index', obj)
    return obj


def extract_name(obj):
    """Extracts name from obj, if any"""
    return getattr(obj, 'name', obj)


def format_duration(obj):
    """Converts obj to consul duration"""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, int):
        return '%ss' % obj
    if isinstance(obj, timedelta):
        return '%ss' % int(obj.total_seconds())
    raise ValueError('wrong type %r' % obj)
