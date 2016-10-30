__all__ = [
    "ConsulError",
    "ConflictError",
    "NotFound",
    "SupportDisabled",
    "TransactionError",
    "UnauthorizedError"
]


class ConsulError(Exception):
    """Consul base error

    Attributes:
        value (Object): object of the error
        meta (Meta): meta of the error
    """
    def __init__(self, msg, *, meta=None):
        self.value = msg
        self.meta = meta or {}
        if isinstance(msg, bytes):
            msg = msg.decode("utf-8")
        super().__init__(msg)


class NotFound(ConsulError):
    """Raised when object does not exists

    Attributes:
        value (Object): object of the error
        meta (Meta): meta of the error
    """


class ConflictError(ConsulError):
    """Raised when there is a conflict in agent

    Attributes:
        value (Object): object of the error
        meta (Meta): meta of the error
    """


class UnauthorizedError(ConsulError):
    """Raised when session with sufficent rights is required

    Attributes:
        value (Object): object of the error
        meta (Meta): meta of the error
    """


class SupportDisabled(Exception):
    """Endpoint is not active.
    """


class TransactionError(Exception):
    """Raised by failing transaction

    Attributes:
        errors (Mapping): The errors where index is the index in operations
        operations (Collection): The operations
        meta (Meta): meta of the error

    For example token has not the sufficient rights for writing key::

        errors = {
            0: {"OpIndex": 0, "What": "Permission denied"}
        }

        operations = [
            {"Verb": "get", "Key": "foo"},
            {"Verb": "set", "Key": "bar", "Value": "YmFy", "Flags": None}
        ]
    """
    def __init__(self, errors, operations, meta, *, msg=None):
        self.errors = errors
        self.operations = operations
        self.meta = meta
        msg = msg or "Transaction failed"
        super().__init__(msg)
