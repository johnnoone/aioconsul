

class ConsulString(str):
    """
    Just a :class:`str` that holds consul meta data.

    Attributes:
        consul (ConsulMeta): consul meta data
    """
    __slots__ = 'consul'


class ConsulMapping(dict):
    """
    Just a :class:`dict` that holds consul meta data.

    Attributes:
        consul (ConsulMeta): consul meta data
    """
    __slots__ = 'consul'


class ConsulSet(set):
    """
    Just a :class:`set` that holds consul meta data.

    Attributes:
        consul (ConsulMeta): consul meta data
    """
    __slots__ = 'consul'
