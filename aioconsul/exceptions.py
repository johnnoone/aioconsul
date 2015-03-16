

class ClientError(Exception):
    pass


class HTTPError(ClientError):
    def __init__(self, status, msg, url, data):
        self.status = status
        self.url = url
        self.data = data
        Exception.__init__(self, msg)


class UnknownLeader(ClientError):
    """Raised when leader is not known (for staleness of data)."""
    pass
