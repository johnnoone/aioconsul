import json

__all__ = ['ConsulMeta', 'DataMapping', 'DataSet', 'render']


class ConsulMeta:
    """
    Attributes:
        modify_index (int): modify index
        last_contact (int): last contact
        known_leader (bool): leader was known while requesting data
    """

    def __init__(self, *, modify_index=None, last_contact=None,
                 known_leader=None):
        self.modify_index = modify_index
        self.last_contact = last_contact
        self.known_leader = known_leader


class DataMapping(dict, ConsulMeta):
    """
    Just a `dict` that holds response headers.

    Attributes:
        modify_index (int): modify index
        last_contact (str): last contact
        known_leader (bool): leader was known while requesting data
    """

    def __init__(self, values, **params):
        super(DataMapping, self).__init__(values)
        ConsulMeta.__init__(self, **params)


class DataSet(set, ConsulMeta):
    """
    Just a `set` that holds response headers.

    Attributes:
        modify_index (int): modify index
        last_contact (str): last contact
        known_leader (bool): leader was known while requesting data
    """

    def __init__(self, values, **params):
        super(DataSet, self).__init__(values)
        ConsulMeta.__init__(self, **params)


def render(values, *, response):
    meta = json.loads(
        '{"modify_index": %s, "last_contact": %s, "known_leader": %s}' % (
            response.headers.get('X-Consul-Index', 'null'),
            response.headers.get('X-Consul-LastContact', 'null'),
            response.headers.get('X-Consul-KnownLeader', 'null')
        )
    )

    if isinstance(values, dict):
        return DataMapping(values, **meta)
    else:
        return DataSet(values, **meta)
