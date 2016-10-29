from collections import namedtuple


Response = namedtuple("Response", "url status body headers method")


class Response:

    def __init__(self, path, status, body, headers, method):
        self.path = path
        self.status = status
        self.body = body
        self.headers = headers
        self.method = method

    def __repr__(self):
        return "<%s(method=%r, path=%r, status=%r, body=%r, headers=%r)>" % (
            self.__class__.__name__,
            self.method,
            self.path,
            self.status,
            self.body,
            self.headers
        )


def extract_body(obj):
    if isinstance(obj, Response):
        return obj.body
    return obj
