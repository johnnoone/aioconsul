from base64 import b64decode, b64encode
import hcl


def encode_value(value, flags=None, base64=False):
    if flags:
        raise ValueError("Don't know how to handle flags %s" % flags)
    elif not isinstance(value, bytes):
        raise ValueError("value must be bytes")
    return b64encode(value) if base64 else value


def decode_value(value, flags=None):
    if flags:
        raise ValueError("Don't know how to handle flags %s" % flags)
    return b64decode(value)


def encode_hcl(value):
    if value is not None and value != "":
        return hcl.dumps(value)
    return value


def decode_hcl(value):
    if value is not None and value != "":
        return hcl.loads(value)
