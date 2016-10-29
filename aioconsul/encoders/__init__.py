from base64 import b64decode, b64encode
import hcl
import logging

logger = logging.getLogger(__name__)


def encode_value(value, flags=None, base64=False):
    """Mostly used by payloads
    """
    if flags:
        # still a no-operation
        logger.debug("Flag %s encoding not implemented yet" % flags)
    if not isinstance(value, bytes):
        raise ValueError("value must be bytes")
    return b64encode(value) if base64 else value


def decode_value(value, flags=None):
    """Mostly used by payloads
    """
    if flags:
        # still a no-operation
        logger.debug("Flag %s decoding not implemented yet" % flags)
    return b64decode(value)


def encode_hcl(value):
    if value is not None and value != "":
        return hcl.dumps(value)
    return value


def decode_hcl(value):
    if value is not None and value != "":
        return hcl.loads(value)
