import asyncio
import logging
from aioconsul.bases import Event
from aioconsul.exceptions import HTTPError, ValidationError

logger = logging.getLogger(__name__)


class EventEndpoint:

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def items(self, *, name=None):
        path = 'event/list'
        params = {'name': name}
        response = yield from self.client.get(path, params=params)
        return {decode(data) for data in (yield from response.json())}

    @asyncio.coroutine
    def fire(self, event, data, *, dc=None,
             node_filter=None, service_filter=None, tag_filter=None):
        path = 'event/fire/%s' % getattr(event, 'name', event)
        params = {'dc': dc, 'node': node_filter,
                  'service': service_filter, 'tag': tag_filter}
        try:
            response = yield from self.client.put(path,
                                                  params=params,
                                                  data=data)
        except HTTPError as error:
            if error.status == 500:
                raise ValidationError(str(error))
            raise
        if response.status == 200:
            return decode((yield from response.json()))


def decode(data):
    return Event(id=data.get('ID'),
                 name=data.get('Name'),
                 payload=data.get('Payload'),
                 node_filter=data.get('NodeFilter'),
                 service_filter=data.get('ServiceFilter'),
                 tag_filter=data.get('TagFilter'),
                 version=data.get('Version'),
                 l_time=data.get('LTime'))
