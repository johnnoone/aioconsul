Misc.
=====



.. currentmodule:: aioconsul.typing

Typing
------

Most of call are polymorphic and most of the types in documentation are just hints.
Here is the full list of types:


.. class:: aioconsul.typing.ObjectIndex

    Used by polymorphic functions that accept any ``str`` or ``dict`` that
    have an **Index** key.

    For example these two objects are equivalent::

        a = { "Index": "1234-43-6789" }
        b = "1234-43-6789"


.. class:: aioconsul.typing.ObjectID

    Used by polymorphic functions that accept any ``str`` or ``dict`` that
    have an **ID** key.

    These two objects are equivalent::

        a = { "ID": "1234-43-6789" }
        b = "1234-43-6789"


.. class:: aioconsul.typing.Object

    Represents a ``dict`` where keys are ``str`` and values can be any type.

    For example::

        {
          "ID": "1234-43-6789",
          "Name": "foo",
          "Value": "bar"
        }

    Depending of the endpoint, **ID** may be required or not.


.. class:: aioconsul.typing.Collection

    Represents a ``list`` where values are :class:`Object`.

    For example::

        [{"ID": "1234"}, {"ID": "5678"}]


.. class:: aioconsul.typing.Mapping

    Represents a ``dict`` where keys are ``id`` and values are :class:`Object`.

    For example::

        {"service1": {"ID": "service1"}}


.. class:: aioconsul.typing.Meta

    Represents a ``dict`` that is associated to Response.
    These keys should be presents:

    * **Index** — a unique identifier representing the current state
      of the requested resource
    * **KnownLeader** — indicates if there is a known leader
    * **LastContact** — Contains the time in milliseconds that a server was
      last contacted by the leader node

    Meta can be used for blocking / watch mode.


.. class:: aioconsul.typing.CollectionMeta

    A tuple where first value is a :class:`Collection` and
    second value is :class:`Meta`.


.. class:: aioconsul.typing.ObjectMeta

    A tuple where first value is an :class:`Object` and
    second value is :class:`Meta`.


.. class:: aioconsul.typing.Filter

    Regular expression to filter by.

    It accepts a ``re.Pattern`` or a ``str``.
    These two objects are equivalent::

        a = re.compile("node-\d+")
        b = "node-\d+"


.. class:: aioconsul.typing.Consistency

    Most of the read query endpoints support multiple levels of consistency.
    Since no policy will suit all clients' needs, these consistency modes
    allow the user to have the ultimate say in how to balance the trade-offs
    inherent in a distributed system. The three read modes are:

    **default** — If not specified, the default is strongly consistent in
    almost all cases. However, there is a small window in which a new leader
    may be elected during which the old leader may service stale values. The
    trade-off is fast reads but potentially stale values. The condition
    resulting in stale reads is hard to trigger, and most clients should not
    need to worry about this case. Also, note that this race condition only
    applies to reads, not writes.

    **consistent** — This mode is strongly consistent without caveats.
    It requires that a leader verify with a quorum of peers that it is still
    leader. This introduces an additional round-trip to all server nodes.
    The trade-off is increased latency due to an extra round trip. Most
    clients should not use this unless they cannot tolerate a stale read.

    **stale** — This mode allows any server to service the read regardless
    of whether it is the leader. This means reads can be arbitrarily stale;
    however, results are generally consistent to within 50 milliseconds of
    the leader. The trade-off is very fast and scalable reads with a higher
    likelihood of stale values. Since this mode allows reads without a
    leader, a cluster that is unavailable will still be able to respond to
    queries.


.. class:: aioconsul.typing.Duration

    Defines a duration. Can be specified in the form of "10s" or "5m" or
    a ``datetime.timedelta``.

    For example, these objects are equivalent::

        timedelta(seconds=150)
        "2m30s"


.. class:: aioconsul.typing.Blocking

    Defines a blocking query.

    It must be a :class:`~aioconsul.typing.ObjectIndex` or better a tuple where
    second value is a :class:`~aioconsul.typing.Duration`.

    For example these values are equivalent::

        a = {"Index": 1}
        b = 1
        c = ({"Index": 1}, None)

    For adding a wait, just set the second value of tuple.


.. class:: aioconsul.typing.Payload

    Currently only ``bytes`` and ``bytearray`` are allowed.
    It may vary on **Flags** value in the futur.

    Internally, Payload will be base64 encoded/decoded when the
    endpoint requires it. End user does not have to do it.

    The :class:`~aioconsul.client.KVEndpoint` is build on top of:

    * ``PUT /v1/kv/(key)`` - **Body** will be encoded
    * ``GET /v1/kv/(key)`` - **Value** will be decoded

    For example::

        PAYLOAD = b"bar"
        await client.kv.set("foo", PAYLOAD)
        response, _ = await client.kv.get("foo")
        assert response["Value"] == PAYLOAD

    The :class:`~aioconsul.client.EventEndpoint` is build on top of:

    * ``PUT /v1/event/fire/(name)`` - **Payload** will be kept as is
    * ``GET /v1/event/list`` - **Payload** will be base64 encoded

    For example::

        PAYLOAD = b"qux"
        response = await client.event.fire("baz", PAYLOAD)
        assert response["Payload"] == PAYLOAD
        responses, _ = await client.kv.items("baz")
        assert responses[0]["Payload"] == PAYLOAD
