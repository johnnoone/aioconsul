from collections.abc import Mapping


def extract_attr(obj, *, keys):
    if isinstance(obj, Mapping):
        for key in keys:
            if key in obj:
                return obj[key]
        raise TypeError("%s not found in obj %s" % (keys, obj))
    return obj


def extract_pattern(obj):
    """Extract pattern from str or re.compile object

    Returns:
        str: Extracted pattern
    """
    if obj is not None:
        return getattr(obj, 'pattern', obj)
    return obj
