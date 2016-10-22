from .bases import EndpointBase
from aioconsul.encoders import decode_value, encode_value
from aioconsul.structures import consul, extract_meta


class EventEndpoint(EndpointBase):

    async def fire(self, name, payload=None, *,
                   dc=None, node=None, service=None, tag=None):
        """Fires a new event

        Parameters:
            name (str): Event name
            payload (bytes): Opaque data
            node (str): Regular expression to filter by node name
            service (str): Regular expression to filter by service
            tag (str): Regular expression to filter by service tags
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
        Returns:
            Object: where value is event ID

        The return body is like::

            {
                "ID": "b54fe110-7af5-cafc-d1fb-afc8ba432b1c",
                "Name": "deploy",
                "Payload": None,
                "NodeFilter": "",
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
        response = await self._api.put(path, data=payload, params={
            "dc": dc, "node": node, "service": service, "tag": tag})
        result = response.body
        if result["Payload"] is not None:
            result["Payload"] = decode_value(result["Payload"])
        return result

    async def items(self, name=None, *, watch=None):
        """Lists the most recent events an agent has seen

        Parameters:
            name (str): Filter events by name.
            watch (Blocking): do a blocking query
        Returns:
            CollectionMeta: where value is a list of events

        It returns a JSON body like this::

            [
                {
                    "ID": "b54fe110-7af5-cafc-d1fb-afc8ba432b1c",
                    "Name": "deploy",
                    "Payload": bytes("abcd"),
                    "NodeFilter": "",
                    "ServiceFilter": "",
                    "TagFilter": "",
                    "Version": 1,
                    "LTime": 19
                },
                ...
            ]
        """
        path = "/v1/event/list"
        response = await self._api.get(path, params={
            "name": name}, watch=watch)
        result = response.body
        for data in result:
            if data["Payload"] is not None:
                data["Payload"] = decode_value(data["Payload"])
        return consul(result, meta=extract_meta(response.headers))
