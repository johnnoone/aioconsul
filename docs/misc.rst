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
