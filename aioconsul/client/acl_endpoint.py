from .bases import EndpointBase
from aioconsul.api import consul, extract_meta
from aioconsul.encoders import encode_hcl, decode_hcl
from aioconsul.exceptions import NotFound
from aioconsul.util import extract_attr


class ACLEndpoint(EndpointBase):
    """Create, update, destroy, and query ACL tokens.

    .. note:: Most of endpoints must be made with a management token.

    """

    async def create(self, token):
        """Creates a new token with a given policy

        Parameters:
            token (Object): Token specification
        Returns:
            Object: token ID

        The create endpoint is used to make a new token.
        A token has a name, a type, and a set of ACL rules.

        The request body may take the form::

            {
                "Name": "my-app-token",
                "Type": "client",
                "Rules": ""
            }

        None of the fields are mandatory. The **Name** and **Rules** fields
        default to being blank, and the **Type** defaults to "client".

        **Name** is opaque to Consul. To aid human operators, it should
        be a meaningful indicator of the ACL's purpose.

        **Type** is either **client** or **management**. A management token
        is comparable to a root user and has the ability to perform any action
        including creating, modifying and deleting ACLs.

        **ID** field may be provided, and if omitted a random UUID will be
        generated.

        The format of **Rules** is
        `documented here <https://www.consul.io/docs/internals/acl.html>`_.

        A successful response body will return the **ID** of the newly
        created ACL, like so::

            {
                "ID": "adf4238a-882b-9ddc-4a9d-5b6758e4159e"
            }
        """
        token = encode_token(token)
        response = await self._api.put("/v1/acl/create", json=token)
        return response.body

    async def update(self, token):
        """Updates the policy of a token

        Parameters:
            token (Object): Token specification
        Returns:
            Object: token ID

        The update endpoint is used to modify the policy for a given ACL
        token. It is very similar to :func:`create()`; however the ID
        field must be provided.

        The body may look like::

            {
                "ID": "adf4238a-882b-9ddc-4a9d-5b6758e4159e",
                "Name": "my-app-token-updated",
                "Type": "client",
                "Rules": "# New Rules",
            }

        Only the **ID** field is mandatory. The other fields provide defaults:
        the **Name** and **Rules** fields default to being blank, and **Type**
        defaults to "client".

        The format of **Rules** is
        `documented here <https://www.consul.io/docs/internals/acl.html>`_.
        """
        token = encode_token(token)
        response = await self._api.put("/v1/acl/create", json=token)
        return response.body

    async def destroy(self, token):
        """Destroys a given token.

        Parameters:
            token (ObjectID): Token ID
        Returns:
            bool: ``True`` on success
        """
        token_id = extract_attr(token, keys=["ID"])
        response = await self._api.put("/v1/acl/destroy", token_id)
        return response.body

    delete = destroy

    async def info(self, token):
        """Queries the policy of a given token.

        Parameters:
            token (ObjectID): Token ID
        Returns:
            ObjectMeta: where value is token
        Raises:
            NotFound:

        It returns a body like this::

            {
                "CreateIndex": 3,
                "ModifyIndex": 3,
                "ID": "8f246b77-f3e1-ff88-5b48-8ec93abf3e05",
                "Name": "Client Token",
                "Type": "client",
                "Rules": {
                    "key": {
                        "": {
                            "policy": "read"
                        },
                        "private/": {
                            "policy": "deny"
                        }
                    }
                }
            }
        """
        token_id = extract_attr(token, keys=["ID"])
        response = await self._api.get("/v1/acl/info", token_id)
        meta = extract_meta(response.headers)
        try:
            result = decode_token(response.body[0])
        except IndexError:
            raise NotFound(response.body, meta=meta)
        return consul(result, meta=meta)

    async def clone(self, token):
        """Creates a new token by cloning an existing token

        Parameters:
            token (ObjectID): Token ID
        Returns:
            ObjectMeta: where value is token ID

        This allows a token to serve as a template for others, making it
        simple to generate new tokens without complex rule management.

        As with create, a successful response body will return the ID of the
        newly created ACL, like so::

            {
                "ID": "adf4238a-882b-9ddc-4a9d-5b6758e4159e"
            }
        """
        token_id = extract_attr(token, keys=["ID"])
        response = await self._api.put("/v1/acl/clone", token_id)
        return consul(response)

    async def items(self):
        """Lists all the active tokens

        Returns:
            ObjectMeta: where value is a list of tokens

        It returns a body like this::

            [
              {
                "CreateIndex": 3,
                "ModifyIndex": 3,
                "ID": "8f246b77-f3e1-ff88-5b48-8ec93abf3e05",
                "Name": "Client Token",
                "Type": "client",
                "Rules": {
                  "key": {
                    "": { "policy": "read" },
                    "private/": { "policy": "deny" }
                  }
                }
              }
            ]
        """
        response = await self._api.put("/v1/acl/list")
        results = [decode_token(r) for r in response.body]
        return consul(results, meta=extract_meta(response.headers))

    async def replication(self, *, dc=None):
        """Checks status of ACL replication

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
        Returns:
            Object: Replication information

        Returns the status of the ACL replication process in the datacenter.
        This is intended to be used by operators, or by automation checking
        the health of ACL replication.

        By default, the datacenter of the agent is queried; however, the dc
        can be provided using the "dc" parameter.

        It returns a body like this::

            {
                "Enabled": True,
                "Running": True,
                "SourceDatacenter": "dc1",
                "ReplicatedIndex": 1976,
                "LastSuccess": datetime(2016, 8, 5, 6, 28, 58, tzinfo=tzutc()),
                "LastError": datetime(2016, 8, 5, 6, 28, 58, tzinfo=tzutc())
            }

        **Enabled** reports whether ACL replication is enabled for the
        datacenter.

        **Running** reports whether the ACL replication process is running.
        The process may take approximately 60 seconds to begin running after
        a leader election occurs.

        **SourceDatacenter** is the authoritative ACL datacenter that ACLs
        are being replicated from, and will match the acl_datacenter
        configuration.

        **ReplicatedIndex** is the last index that was successfully replicated.
        You can compare this to the Index meta returned by the items() endpoint
        to determine if the replication process has gotten all available ACLs.
        Note that replication runs as a background process approximately every
        30 seconds, and that local updates are rate limited to 100
        updates/second, so so it may take several minutes to perform the
        initial sync of a large set of ACLs. After the initial sync, replica
        lag should be on the order of about 30 seconds.

        **LastSuccess** is the UTC time of the last successful sync operation.
        Note that since ACL replication is done with a blocking query, this
        may not update for up to 5 minutes if there have been no ACL changes
        to replicate. A zero value of "0001-01-01T00:00:00Z" will be present
        if no sync has been successful.

        **LastError** is the UTC time of the last error encountered during a
        sync operation. If this time is later than LastSuccess, you can assume
        the replication process is not in a good state. A zero value of
        "0001-01-01T00:00:00Z" will be present if no sync has resulted in an
        error.
        """
        params = {"dc": dc}
        response = await self._api.get("/v1/acl/replication", params=params)
        return response.body


def decode_token(token):
    result = {}
    result.update(token)
    result["Rules"] = decode_hcl(token["Rules"])
    return result


def encode_token(token):
    result = {}
    result.update(token)
    rules = token.get("Rules")
    if rules is not None and not isinstance(rules, str):
        result["Rules"] = encode_hcl(rules)
    return result
