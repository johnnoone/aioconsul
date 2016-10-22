from .bases import EndpointBase
from .util import prepare_node, prepare_service, prepare_check
from aioconsul.common import extract_id
from aioconsul.structures import consul


class CatalogEndpoint(EndpointBase):

    async def register_node(self, node):
        """Registers a node

        Parameters:
            node (Object): Node definition
        Returns:
            bool: ``True`` on success
        """
        return await self.register(node)

    async def register_check(self, node, *, check):
        """Registers a check

        Parameters:
            node (Object): Node definition
            check (Object): Check definition
        Returns:
            bool: ``True`` on success
        """
        return await self.register(node, check=check)

    async def register_service(self, node, *, service):
        """Registers a service

        Parameters:
            node (Object): Node definition
            service (Object): Service definition
        Returns:
            bool: ``True`` on success
        """
        return await self.register(node, service=service)

    async def register(self, node, *,
                       check=None, service=None, write_token=None):
        """Registers a new node, service or check

        Parameters:
            node (Object): Node definition
            check (Object): Check definition
            service (Object or ObjectID): service
            write_token (ObjectID): token ID
        Returns:
            bool: ``True`` on success

        .. note:: it is usually preferrable instead to use the agent
                  endpoints for registration as they are simpler and
                  perform anti-entropy.

        **Node** body must look something like::

            {
                "Datacenter": "dc1",
                "Node": "foobar",
                "Address": "192.168.10.10",
                "TaggedAddresses": {
                    "lan": "192.168.10.10",
                    "wan": "10.0.10.10"
                }
            }

        **Service** body must look something like::

            {
                "ID": "redis1",
                "Service": "redis",
                "Tags": [
                    "master",
                    "v1"
                ],
                "Address": "127.0.0.1",
                "Port": 8000
            }

        **Check** body must look something like::

            {
                "Node": "foobar",
                "CheckID": "service:redis1",
                "Name": "Redis health check",
                "Notes": "Script based health check",
                "Status": "passing",
                "ServiceID": "redis1"
            }

        The behavior of the endpoint depends on what parameters are provided.

        **Node** and **Address** fields are required, while
        **Datacenter** will be defaulted to match that of the agent.
        If only those are provided, the endpoint will register the
        node with the catalog.
        **TaggedAddresses** can be used in conjunction with the
        translate_wan_addrs configuration option and the "wan" address.

        If the **Service** key is provided, the service will also be
        registered. If **ID** is not provided, it will be defaulted to the
        value of the **Service.Service** property. Only one service with a
        given **ID** may be present per node. The service **Tags**,
        **Address**, and **Port** fields are all optional.

        If the **Check** key is provided, a health check will also be
        registered.

        .. note:: This register API manipulates the health check entry in
                  the Catalog, but it does not setup the script, **TTL**,
                  or **HTTP** check to monitor the node's health. To truly
                  enable a new health check, the check must either be provided
                  in agent configuration or set via the agent endpoint.

        The **CheckID** can be omitted and will default to the value of
        **Name**. As with **Service.ID**, the **CheckID** must be unique on
        this node. **Notes** is an opaque field that is meant to hold
        human-readable text. If a **ServiceID** is provided that matches the
        **ID** of a service on that node, the check is treated as a service
        level health check, instead of a node level health check. The
        **Status** must be one of ``passing``, ``warning``, or ``critical``.

        Multiple checks can be provided by replacing **Check** with **Checks**
        and sending a list of Check objects.

        It is important to note that **Check** does not have to be provided
        with **Service** and vice versa. A catalog entry can have either,
        neither, or both.

        An optional ACL token may be provided to perform the registration by
        including a **WriteRequest** block in the query payload, like this::

            {
                "WriteRequest": {
                    "Token": "foo"
                }
            }
        """
        node_id, node = prepare_node(node)
        service_id, service = prepare_service(service)
        _, check = prepare_check(check)
        if check and node_id:
            check["Node"] = node_id
        if check and service_id:
            check["ServiceID"] = service_id
        token = extract_id(write_token)
        entry = node
        if service:
            entry["Service"] = service
        if check:
            entry["Check"] = check
        if token:
            entry["WriteRequest"] = {
                "Token": token
            }
        response = await self._api.put("/v1/catalog/register", json=entry)
        return response.status == 200

    async def deregister_node(self, node):
        """Deregisters a node

        Parameters:
            node (ObjectID): node ID
        Returns:
            bool: ``True`` on success
        """
        return await self.deregister(node)

    async def deregister_check(self, node, *, check):
        """Deregisters a check

        Parameters:
            node (ObjectID): node ID
            check (ObjectID): check ID
        Returns:
            bool: ``True`` on success
        """
        return await self.deregister(node, check=check)

    async def deregister_service(self, node, *, service):
        """Deregisters a service

        Parameters:
            node (ObjectID): node ID
            service (ObjectID): service ID
        Returns:
            bool: ``True`` on success
        """
        return await self.deregister(node, service=service)

    async def deregister(self, node, *,
                         check=None, service=None, write_token=None):
        """Deregisters a node, service or check

        Parameters:
            node (Object or ObjectID): node
            check (ObjectID): check ID
            service (ObjectID): service ID
            write_token (ObjectID): token ID
        Returns:
            bool: ``True`` on success

        **Node** expects a body that look like one of the following::

            {
                "Datacenter": "dc1",
                "Node": "foobar",
            }

        ::

            {
                "Datacenter": "dc1",
                "Node": "foobar",
                "CheckID": "service:redis1"
            }

        ::

            {
              "Datacenter": "dc1",
              "Node": "foobar",
              "ServiceID": "redis1",
            }

        The behavior of the endpoint depends on what keys are provided.
        The endpoint requires **Node** to be provided while **Datacenter**
        will be defaulted to match that of the agent. If only **Node** is
        provided, the node and all associated services and checks are deleted.
        If **CheckID** is provided, only that check is removed.
        If **ServiceID** is provided, the service and its associated health
        check (if any) are removed.

        An optional ACL token may be provided to perform the deregister action
        by adding a **WriteRequest** block to the payload, like this::

            {
                "WriteRequest": {
                    "Token": "foo"
                }
            }
        """
        entry = {}
        if isinstance(node, str):
            entry["Node"] = node
        else:
            for k in ("Datacenter", "Node", "CheckID",
                      "ServiceID", "WriteRequest"):
                if k in node:
                    entry[k] = node[k]
        service_id = extract_id(service, keys=["ServiceID", "ID"])
        check_id = extract_id(check, keys=["CheckID", "ID"])
        if service_id and not check_id:
            entry["ServiceID"] = service_id
        elif service_id and check_id:
            entry["CheckID"] = "%s:%s" % (service_id, check_id)
        elif not service_id and check_id:
            entry["CheckID"] = check_id
        if write_token:
            entry["WriteRequest"] = {
                "Token": extract_id(write_token)
            }
        response = await self._api.put("/v1/catalog/deregister", json=entry)
        return response.status == 200

    async def datacenters(self):
        """Lists known datacenters

        Returns:
            Collection: collection of datacenters

        The datacenters will be sorted in ascending order based on the
        estimated median round trip time from the server to the servers
        in that datacenter.

        For example::

            [
              "dc1",
              "dc2"
            ]
        """
        response = await self._api.get("/v1/catalog/datacenters")
        return response.body

    async def nodes(self, *,
                    dc=None, near=None, watch=None, consistency=None):
        """Lists nodes in a given DC

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            near (str): Sort the node list in ascending order based on the
                        estimated round trip time from that node.
            watch (Blocking): do a blocking query
            consistency (Consistency): force consistency
        Returns:
            CollectionMeta: where value is a list

        It returns a body like this::

            [
              {
                "Node": "baz",
                "Address": "10.1.10.11",
                "TaggedAddresses": {
                  "lan": "10.1.10.11",
                  "wan": "10.1.10.11"
                }
              },
              {
                "Node": "foobar",
                "Address": "10.1.10.12",
                "TaggedAddresses": {
                  "lan": "10.1.10.11",
                  "wan": "10.1.10.12"
                }
              }
            ]
        """
        response = await self._api.get("/v1/catalog/nodes", params={
            "dc": dc, "near": near}, watch=watch, consistency=consistency)
        return consul(response)

    async def services(self, *, dc=None, watch=None, consistency=None):
        """Lists services in a given DC

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): do a blocking query
            consistency (Consistency): force consistency
        Returns:
            ObjectMeta: where value is a dict

        It returns a JSON body like this::

            {
              "consul": [],
              "redis": [],
              "postgresql": [
                "master",
                "slave"
              ]
            }

        The keys are the service names, and the array values provide all known
        tags for a given service.
        """
        response = await self._api.get("/v1/catalog/services", params={
            "dc": dc}, watch=watch, consistency=consistency)
        return consul(response)

    async def service(self, service, *,
                      tag=None, dc=None, near=None,
                      watch=None, consistency=None):
        """Lists the nodes providing a service in a given datacenter

        Parameters:
            service (ObjectID): service ID
            tag (str): Filter the list by tag.
                       By default all nodes in that service are returned.
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            near (str): Sort the node list in ascending order based on
                        the estimated round trip time from that node.
            watch (Blocking): do a blocking query
            consistency (Consistency): force consistency
        Returns:
            CollectionMeta: where value is a list of nodes/services

        It returns a body like this::

            [
              {
                "Node": "foobar",
                "Address": "10.1.10.12",
                "ServiceID": "redis",
                "ServiceName": "redis",
                "ServiceTags": None,
                "ServiceAddress": "",
                "ServicePort": 8000
              }
            ]
        """
        service_id = extract_id(service, keys=["ServiceID", "ID"])
        response = await self._api.get(
            "/v1/catalog/service", service_id,
            params={"dc": dc, "tag": tag, "near": near},
            watch=watch, consistency=consistency)
        return consul(response)

    async def node(self, node, *, dc=None, watch=None, consistency=None):
        """Lists the services provided by a node

        Parameters:
            node (ObjectID): the node ID
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): do a blocking query
            consistency (Consistency): force consistency
        Returns:
            ObjectMeta: where value is node or None if does not exists

        It returns a body like this::

            {
              "Node": {
                "Node": "foobar",
                "Address": "10.1.10.12",
                "TaggedAddresses": {
                  "lan": "10.1.10.12",
                  "wan": "10.1.10.12"
                }
              },
              "Services": {
                "consul": {
                  "ID": "consul",
                  "Service": "consul",
                  "Tags": None,
                  "Port": 8300
                },
                "redis": {
                  "ID": "redis",
                  "Service": "redis",
                  "Tags": ["v1"],
                  "Port": 8000
                }
              }
            }
        """
        node_id = extract_id(node, keys=["Node", "ID"])

        response = await self._api.get("/v1/catalog/node/", node_id, params={
            "dc": dc}, watch=watch, consistency=consistency)
        return consul(response)
