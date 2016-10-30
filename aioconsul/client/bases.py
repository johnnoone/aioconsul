

class EndpointBase:

    def __init__(self, api):
        self._api = api

    def __repr__(self):
        return "<%s(%r)>" % (self.__class__.__name__, str(self._api.address))
