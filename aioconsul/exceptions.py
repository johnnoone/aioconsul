__all__ = [
    "ConsulError",
    "ConflictError",
    "NotFound",
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


class TransactionError(Exception):
    """Raised by failing transaction

    Attributes:
        errors (dict): The errors
        operations (list): The operations
        meta (Meta): meta of the error
    """

    def __init__(self, errors, operations, meta, *, msg=None):
        self.errors = errors
        self.operations = operations
        self.meta = meta
        msg = msg or "Transaction failed"
        super().__init__(msg)
