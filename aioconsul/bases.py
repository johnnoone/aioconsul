from collections import namedtuple

__all__ = ['ACL', 'Rule', 'Check', 'Event', 'Member',
           'Node', 'Service', 'NodeService']


class ACL:

    def __init__(self, id, *, name, type, rules,
                 create_index=None, modify_index=None):
        self.id = id
        self.name = name
        self.type = type
        self.rules = rules or []
        self.create_index = create_index
        self.modify_index = modify_index

    def __iter__(self):
        return iter(self.rules)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<ACL(id=%r, name=%r)>' % (self.id, self.name)

Rule = namedtuple('Rule', 'type value policy')


class Check:

    def __init__(self, id, *, name, status=None, notes=None,
                 output=None, service_id=None, service_name=None, node=None):
        self.id = id
        self.name = name
        self.status = status
        self.notes = notes
        self.output = output
        self.service_id = service_id
        self.service_name = service_name
        self.node = node

    def __repr__(self):
        return '<Check(id=%r, name=%r)>' % (self.id, self.name)


class Event(object):

    def __init__(self, name, *, id=None, payload=None,
                 node_filter=None, service_filter=None, tag_filter=None,
                 version=None, l_time=None):
        self.id = id
        self.name = name
        self.payload = payload
        self.node_filter = node_filter
        self.service_filter = service_filter
        self.tag_filter = tag_filter
        self.version = version
        self.l_time = l_time

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<Event(id=%r, name=%r)>' % (self.id, self.name)


class Member:
    def __init__(self, name, address, port, **params):
        self.name = name
        self.address = name
        self.port = port
        for k, v in params.items():
            setattr(self, k, v)

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return '<Member(name=%r, address=%r, port=%r)>' % (
            self.name, self.address, self.port)


class Node:

    def __init__(self, name, address):
        self.name = name
        self.address = address

    def __iter__(self):
        if hasattr(self, 'service'):
            return iter([self.service])
        if hasattr(self, 'services'):
            return self.services.values()
        raise TypeError('Does not have service nor services')

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return '<Node(name=%r)>' % self.name


class Service:

    def __init__(self, id, *, name):
        self.id = id
        self.name = name

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return '<Service(id=%r)>' % self.id


class NodeService(Service):
    """A service that belongs to a node."""

    def __init__(self, id, *, name, address=None, port=None, tags=None):
        Service.__init__(self, id, name=name)
        self.address = address
        self.port = port
        self.tags = tags

    def __repr__(self):
        return '<NodeService(id=%r)>' % self.id


class KeyMeta:

    def __init__(self, key, *, create_index, lock_index, modify_index):
        self.key = key
        self.create_index = create_index
        self.lock_index = lock_index
        self.modify_index = modify_index

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return '<KeyMeta(key=%r)>' % self.key
