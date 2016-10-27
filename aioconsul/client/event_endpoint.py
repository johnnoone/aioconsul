import re
from .bases import EndpointBase
from aioconsul.api import consul, extract_meta
from aioconsul.encoders import decode_value, encode_value
from aioconsul.util import extract_pattern


class EventEndpoint(EndpointBase):

    async def fire(self, name, payload=None, *,
                   dc=None, node=None, service=None, tag=None):
        """Fires a new event

        Parameters:
            name (str): Event name
            payload (Payload): Opaque data
            node (Filter): Regular expression to filter by node name
            service (Filter): Regular expression to filter by service
            tag (Filter): Regular expression to filter by service tags
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
        Returns:
            Object: where value is event ID

        The return body is like::

            {
                "ID": "b54fe110-7af5-cafc-d1fb-afc8ba432b1c",
                "Name": "deploy",
                "Payload": None,
                "NodeFilter": re.compile("node-\d+"),
                "ServiceFilter": "",
                "TagFilter": "",
                "Version": 1,
                "LTime": 0
            }

        The **ID** field uniquely identifies the newly fired event.
        """
        if payload:
            payload = encode_value(payload)

        path = "/v1/event/fire/%s" % name
        params = {
            "dc": dc,
            "node": extract_pattern(node),
            "service": extract_pattern(service),
            "tag": extract_pattern(tag)
        }
        response = await self._api.put(path, data=payload, params=params)
        result = format_event(response.body)
        return result

    async def items(self, name=None, *, watch=None):
        """Lists the most recent events an agent has seen

        Parameters:
            name (str): Filter events by name.
            watch (Blocking): Do a blocking query
        Returns:
            CollectionMeta: where value is a list of events

        It returns a JSON body like this::

            [
                {
                    "ID": "b54fe110-7af5-cafc-d1fb-afc8ba432b1c",
                    "Name": "deploy",
                    "Payload": bytes("abcd"),
                    "NodeFilter": re.compile("node-\d+"),
                    "ServiceFilter": "",
                    "TagFilter": "",
                    "Version": 1,
                    "LTime": 19
                },
                ...
            ]
        """
        path = "/v1/event/list"
        params = {"name": name}
        response = await self._api.get(path, params=params, watch=watch)
        results = [format_event(data) for data in response.body]
        return consul(results, meta=extract_meta(response.headers))


def format_event(obj):
    result = {}
    result.update(obj)
    if obj["Payload"] is not None:
        result["Payload"] = decode_value(obj["Payload"])
    for key in ("NodeFilter", "ServiceFilter", "TagFilter"):
        result[key] = re.compile(obj[key]) if obj.get(key) else None
    return result
