

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


class Node:

    def __init__(self, name, address):
        self.name = name
        self.address = address

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
