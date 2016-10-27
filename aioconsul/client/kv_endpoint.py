from .bases import EndpointBase
from aioconsul.api import consul, extract_meta
from aioconsul.encoders import decode_value, encode_value
from aioconsul.util import extract_attr


class ReadMixin:

    async def _read(self, path, *,
                    raw=None,
                    recurse=None,
                    dc=None,
                    separator=None,
                    keys=None,
                    watch=None,
                    consistency=None):
        """Returns the specified key

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        """
        response = await self._api.get(
            "/v1/kv", path,
            params={
                "raw": raw,
                "dc": dc,
                "recurse": recurse,
                "separator": separator,
                "keys": keys
            },
            watch=watch,
            consistency=consistency)
        return response

    async def keys(self, prefix, *,
                   dc=None, separator=None, watch=None, consistency=None):
        """Returns a list of the keys under the given prefix

        Parameters:
            prefix (str): Prefix to fetch
            separator (str): List only up to a given separator
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            CollectionMeta: where value is list of keys

        For example, listing ``/web/`` with a ``/`` separator may return::

            [
              "/web/bar",
              "/web/foo",
              "/web/subdir/"
            ]

        """
        response = await self._read(prefix,
                                    dc=dc,
                                    separator=separator,
                                    keys=True,
                                    watch=watch,
                                    consistency=consistency)
        return consul(response)

    async def get(self, key, *, dc=None, watch=None, consistency=None):
        """Returns the specified key

        Parameters:
            key (str): Key to fetch
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            ObjectMeta: where value is the queried kv value

        Object will look like::

            {
                "CreateIndex": 100,
                "ModifyIndex": 200,
                "LockIndex": 200,
                "Key": "zip",
                "Flags": 0,
                "Value": b"my data",
                "Session": "adf4238a-882b-9ddc-4a9d-5b6758e4159e"
            }

        **CreateIndex** is the internal index value that represents when
        the entry was created.

        **ModifyIndex** is the last index that modified this key.
        This index corresponds to the X-Consul-Index header value that is
        returned in responses, and it can be used to establish blocking
        queries. You can even perform blocking queries against entire
        subtrees of the KV store.

        **LockIndex** is the number of times this key has successfully been
        acquired in a lock. If the lock is held, the Session key provides
        the session that owns the lock.

        **Key** is simply the full path of the entry.

        **Flags** is an opaque unsigned integer that can be attached to each
        entry. Clients can choose to use this however makes sense for their
        application.

        **Value** is a :class:`~aioconsul.typing.Payload` object,
        it depends on **Flags**.
        """
        response = await self._read(key,
                                    dc=dc,
                                    watch=watch,
                                    consistency=consistency)
        result = response.body[0]
        result["Value"] = decode_value(result["Value"], result["Flags"])
        return consul(result, meta=extract_meta(response.headers))

    async def raw(self, key, *, dc=None, watch=None, consistency=None):
        """Returns the specified key

        Parameters:
            key (str): Key to fetch
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            ObjectMeta: where value is the raw value
        """
        response = await self._read(key,
                                    dc=dc,
                                    raw=True,
                                    watch=watch,
                                    consistency=consistency)
        return consul(response)

    async def get_tree(self, prefix, *,
                       dc=None, separator=None, watch=None, consistency=None):
        """Gets all keys with a prefix of Key during the transaction.

        Parameters:
            prefix (str): Prefix to fetch
            separator (str): List only up to a given separator
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency
        Returns:
            CollectionMeta: where value is a list of values

        This does not fail the transaction if the Key doesn't exist. Not
        all keys may be present in the results if ACLs do not permit them
        to be read.
        """
        response = await self._read(prefix,
                                    dc=dc,
                                    recurse=True,
                                    separator=separator,
                                    watch=watch,
                                    consistency=consistency)
        result = response.body
        for data in result:
            data["Value"] = decode_value(data["Value"], data["Flags"])
        return consul(result, meta=extract_meta(response.headers))


class WriteMixin:

    async def set(self, key, value, *, flags=None):
        """Sets the key to the given value.

        Parameters:
            key (str): Key to set
            value (Payload): Value to set, It will be encoded by flags
            flags (int): Flags to set with value
        Returns:
            bool: ``True`` on success
        """
        value = encode_value(value, flags)
        response = await self._write(key, value, flags=flags)
        return response.body is True

    async def cas(self, key, value, *, flags=None, index):
        """Sets the key to the given value with check-and-set semantics.

        Parameters:
            key (str): Key to set
            value (Payload): Value to set, It will be encoded by flags
            index (ObjectIndex): Index ID
            flags (int): Flags to set with value
        Response:
            bool: ``True`` on success

        The Key will only be set if its current modify index matches
        the supplied Index

        If the index is 0, Consul will only put the key if it does not already
        exist. If the index is non-zero, the key is only set if the index
        matches the ModifyIndex of that key.
        """
        value = encode_value(value, flags)
        index = extract_attr(index, keys=["ModifyIndex", "Index"])
        response = await self._write(key, value, flags=flags, cas=index)
        return response.body is True

    async def lock(self, key, value, *, flags=None, session):
        """Locks the Key with the given Session.

        Parameters:
            key (str): Key to set
            value (Payload): Value to set, It will be encoded by flags
            session (ObjectID): Session ID
            flags (int): Flags to set with value
        Response:
            bool: ``True`` on success

        The Key will only obtain the lock if the Session is valid, and no
        other session has it locked
        """
        value = encode_value(value, flags)
        session_id = extract_attr(session, keys=["ID"])
        response = await self._write(key, value,
                                     flags=flags,
                                     acquire=session_id)
        return response.body is True

    async def unlock(self, key, value, *, flags=None, session):
        """Unlocks the Key with the given Session.

        Parameters:
            key (str): Key to set
            value (Payload): Value to set, It will be encoded by flags
            session (ObjectID): Session ID
            flags (int): Flags to set with value
        Response:
            bool: ``True`` on success

        The Key will only release the lock if the Session is valid and
        currently has it locked.
        """
        value = encode_value(value, flags)
        session_id = extract_attr(session, keys=["ID"])
        response = await self._write(key, value,
                                     flags=flags,
                                     release=session_id)
        return response.body is True

    async def _write(self, path, data, *,
                     flags=None, cas=None, acquire=None, release=None):
        """Sets the key to the given value.

        Returns:
            bool: ``True`` on success
        """
        if not isinstance(data, bytes):
            raise ValueError("value must be bytes")
        path = "/v1/kv/%s" % path
        response = await self._api.put(path, params={
            "flags": flags,
            "cas": cas,
            "acquire": acquire,
            "release": release
        }, data=data)
        return response


class DeleteMixin:

    async def delete(self, key):
        """Deletes the Key

        Parameters:
            key (str): Key to delete
        Response:
            bool: ``True`` on success
        """
        response = await self._discard(key)
        return response.body is True

    async def delete_tree(self, prefix, *, separator=None):
        """Deletes all keys with a prefix of Key.

        Parameters:
            key (str): Key to delete
            separator (str): Delete only up to a given separator
        Response:
            bool: ``True`` on success
        """
        response = await self._discard(prefix,
                                       recurse=True,
                                       separator=separator)
        return response.body is True

    async def delete_cas(self, key, *, index):
        """Deletes the Key with check-and-set semantics.

        Parameters:
            key (str): Key to delete
            index (ObjectIndex): Index ID
        Response:
            bool: ``True`` on success

        The Key will only be deleted if its current modify index matches the
        supplied Index.
        """
        index = extract_attr(index, keys=["ModifyIndex", "Index"])
        response = await self._discard(key, cas=index)
        return response.body is True

    async def _discard(self, path, *, recurse=None, separator=None, cas=None):
        """Deletes the Key
        """
        path = "/v1/kv/%s" % path
        response = await self._api.delete(path, params={
            "cas": cas,
            "recurse": recurse,
            "separator": separator
        })
        return response


class KVEndpoint(EndpointBase, ReadMixin, WriteMixin, DeleteMixin):

    def prepare(self):
        """Prepare a transaction

        Returns:
            KVOperations: a transaction object
        """
        return KVOperations(self._api)


class KVOperations(EndpointBase):
    """Manages updates or fetches of multiple keys inside a single,
    atomic transaction
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operations = []

    def append(self, operation):
        """Appends a new KV operation to session.
        """
        self.operations.append({"KV": operation})
        return self

    def set(self, key, value, *, flags=None):
        """Sets the Key to the given Value

        Parameters:
            key (str): Key to set
            value (Payload): Value to set, It will be encoded by flags
            flags (int): Flags to set with value
        """
        self.append({
            "Verb": "set",
            "Key": key,
            "Value": encode_value(value, flags, base64=True).decode("utf-8"),
            "Flags": flags
        })
        return self

    def cas(self, key, value, *, flags=None, index):
        """Sets the Key to the given Value with check-and-set semantics

        Parameters:
            key (str): Key to set
            value (Payload): Value to set, It will be encoded by flags
            index (ObjectIndex): Index ID
            flags (int): Flags to set with value

        The Key will only be set if its current modify index matches the
        supplied Index
        """
        self.append({
            "Verb": "cas",
            "Key": key,
            "Value": encode_value(value, flags, base64=True).decode("utf-8"),
            "Flags": flags,
            "Index": extract_attr(index, keys=["ModifyIndex", "Index"])
        })
        return self

    def lock(self, key, value, *, flags=None, session):
        """Locks the Key with the given Session

        Parameters:
            key (str): Key to set
            value (Payload): Value to set, It will be encoded by flags
            session (ObjectID): Session ID

        The Key will only be set if its current modify index matches the
        supplied Index
        """
        self.append({
            "Verb": "lock",
            "Key": key,
            "Value": encode_value(value, flags, base64=True).decode("utf-8"),
            "Flags": flags,
            "Session": extract_attr(session, keys=["ID"])
        })
        return self

    def unlock(self, key, value, *, flags=None, session):
        """Unlocks the Key with the given Session

        Parameters:
            key (str): Key to set
            value (Payload): Value to set, It will be encoded by flags
            session (ObjectID): Session ID

        The Key will only release the lock if the Session is valid and
        currently has it locked.
        """
        self.append({
            "Verb": "unlock",
            "Key": key,
            "Value": encode_value(value, flags, base64=True).decode("utf-8"),
            "Flags": flags,
            "Session": extract_attr(session, keys=["ID"])
        })
        return self

    def get(self, key):
        """Gets the Key during the transaction

        Parameters:
            key (str): Key to fetch
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency

        This fails the transaction if the Key doesn't exist. The key may not
        be present in the results if ACLs do not permit it to be read.
        """
        self.append({
            "Verb": "get",
            "Key": key
        })
        return self

    def get_tree(self, key):
        """Gets all keys with a prefix of Key during the transaction

        Parameters:
            prefix (str): Prefix to fetch
            separator (str): List only up to a given separator
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            watch (Blocking): Do a blocking query
            consistency (Consistency): Force consistency

        This does not fail the transaction if the Key doesn't exist. Not all
        keys may be present in the results if ACLs do not permit them to be
        read.
        """
        self.append({
            "Verb": "get-tree",
            "Key": key
        })
        return self

    def check_index(self, key, *, index):
        """Fails the transaction if Key does not have a modify index equal to
        Index

        Parameters:
            key (str): Key to check
            index (ObjectIndex): Index ID
        """
        self.append({
            "Verb": "check-index",
            "Key": key,
            "Index": extract_attr(index, keys=["ModifyIndex", "Index"])
        })
        return self

    def check_session(self, key, *, session=None):
        """Fails the transaction if Key is not currently locked by Session

        Parameters:
            key (str): Key to check
            session (ObjectID): Session ID
        """
        self.append({
            "Verb": "check-session",
            "Key": key,
            "Session": extract_attr(session, keys=["ID"])
        })
        return self

    def delete(self, key):
        """Deletes the Key

        Parameters:
            key (str): Key to delete
        """
        self.append({
            "Verb": "delete",
            "Key": key
        })
        return self

    def delete_tree(self, key):
        """Deletes all keys with a prefix of Key

        Parameters:
            key (str): Key to delete
            separator (str): Delete only up to a given separator
        """
        self.append({
            "Verb": "delete-tree",
            "Key": key
        })
        return self

    def delete_cas(self, key, *, index):
        """Deletes the Key with check-and-set semantics.

        Parameters:
            key (str): Key to delete
            index (ObjectIndex): Index ID

        The Key will only be deleted if its current modify index matches
        the supplied Index
        """
        self.append({
            "Verb": "delete-cas",
            "Key": key,
            "Index": extract_attr(index, keys=["ModifyIndex", "Index"])
        })
        return self

    async def execute(self, dc=None, token=None):
        """Execute stored operations

        Parameters:
            dc (str): Specify datacenter that will be used.
                      Defaults to the agent's local datacenter.
            token (ObjectID): Token ID
        Returns:
            Collection: Results of operations.
        """
        token_id = extract_attr(token, keys=["ID"])
        try:
            response = await self._api.put(
                "/v1/txn",
                json=self.operations,
                params={
                    "dc": dc,
                    "token": token_id
                })
        except Exception as error:
            raise error
        else:
            self.operations[:] = []

        results = []
        for _ in response.body["Results"]:
            data = _["KV"]
            if data["Value"] is not None:
                data["Value"] = decode_value(data["Value"], data["Flags"])
            results.append(data)
        return results
