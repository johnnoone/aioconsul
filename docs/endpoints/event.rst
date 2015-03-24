.. py:module:: aioconsul
.. _event:

Event
=====

The Event endpoint is used to fire new events and to query the available events.

Fires a new user event::

    >>> event = yield from client.events.fire('my-event-b', 'my-payload')

Lists the most recent events an agent has seen::

    >>> events = yield from client.events('my-event')


Internals
---------

.. autoclass:: aioconsul.EventEndpoint
   :members:
