import asyncio
import logging
from aioconsul.bases import Event
from aioconsul.exceptions import HTTPError, ValidationError
from aioconsul.response import render, render_meta
from aioconsul.util import extract_name, task

logger = logging.getLogger(__name__)


class EventEndpoint:

    def __init__(self, client, *, loop=None):
        self.client = client
        self.loop = loop or asyncio.get_event_loop()

    @task
    def items(self, *, event=None):
        """Lists latest events.

        Parameters:
            event (str): filter by event
        Returns:
            set: set of :class:`Event`
        """
        path = 'event/list'
        params = {}
        if event:
            params['name'] = extract_name(event)

        response = yield from self.client.get(path, params=params)
        values = {decode(data) for data in (yield from response.json())}
        return render(values, response=response)

    __call__ = items

    @task
    def fire(self, event, payload, *, dc=None,
             node_filter=None, service_filter=None, tag_filter=None):
        """Fires a new event.

        Parameters:
            event (str): name of the event
            payload (str): content to send
            dc (str): Select a datacenter
            node_filter (str): Filter to these nodes
            service_filter (str): Filter to these services
            tag_filter (str): Filter to these tags
        Returns:
            Event: instance
        Raises:
            ValidationError: an error occured
        """
        path = 'event/fire/%s' % extract_name(event)
        params = {'dc': dc, 'node': node_filter,
                  'service': service_filter, 'tag': tag_filter}
        response = yield from self.client.put(path,
                                              params=params,
                                              data=payload)
        if response.status == 200:
            return decode((yield from response.json()))

        msg = yield from response.text()
        if response.status == 500:
            err = ValidationError(msg)
        else:
            err = HTTPError(msg, response.status)
        err.consul = render_meta(response)
        raise err


def decode(data):
    return Event(id=data.get('ID'),
                 name=data.get('Name'),
                 payload=data.get('Payload'),
                 node_filter=data.get('NodeFilter'),
                 service_filter=data.get('ServiceFilter'),
                 tag_filter=data.get('TagFilter'),
                 version=data.get('Version'),
                 l_time=data.get('LTime'))
