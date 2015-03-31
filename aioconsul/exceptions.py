"""
    Exceptions
    ~~~~~~~~~~
"""


class ClientError(Exception):
    pass


class HTTPError(ClientError):

    def __init__(self, msg, status):
        self.status = status
        ClientError.__init__(self, msg)


class PermissionDenied(Exception):
    """Raised when client has not good ACL."""
    pass


class SupportDisabled(ClientError):
    """Raised when client does not support ACL."""
    pass


# high level

class ValidationError(ValueError):
    """Raised when something does not validate.
    """
    pass
