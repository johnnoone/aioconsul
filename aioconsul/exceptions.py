"""
    Exceptions
    ~~~~~~~~~~
"""


class ClientError(Exception):
    pass


class HTTPError(ClientError):

    def __init__(self, status, msg, url, data, headers):
        self.status = status
        self.url = url
        self.data = data
        self.headers = headers
        ClientError.__init__(self, msg)


class UnknownLeader(HTTPError):
    """Raised when leader is not known (for staleness of data)."""
    pass


class ACLPermissionDenied(HTTPError):
    """docstring for ACLPermissionDenied"""
    pass


class ACLSupportDisabled(ClientError):
    """Raised when client does not support ACL."""
    pass


# high level

class ValidationError(ValueError):
    """Raised when something does not validate.
    """
    pass
