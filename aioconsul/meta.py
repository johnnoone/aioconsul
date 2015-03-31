

class ConsulMeta:
    """
    Attributes:
        last_index (int): modify index
        last_contact (int): last contact
        known_leader (bool): leader was known while requesting data
    """

    def __init__(self, *, last_index=None, last_contact=None,
                 known_leader=None):
        self.last_index = last_index
        self.last_contact = last_contact
        self.known_leader = known_leader

    @property
    def modify_index(self):
        # alias of last_index
        return self.last_index

    def __repr__(self):
        return '<ConsulMeta(last_index=%r)>' % self.last_index
