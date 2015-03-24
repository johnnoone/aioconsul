import asyncio
import copy
import json
import logging
from aioconsul.bases import Session
from aioconsul.response import render
from aioconsul.util import format_duration, extract_id, extract_name

log = logging.getLogger(__name__)


class SessionEndpoint:

    class NotFound(ValueError):
        """Raised when session was not found"""

    def __init__(self, client, dc=None):
        self.client = client
        self.dc = dc

    def dc(self, name):
        """
        Wraps next requests to the specified datacenter.

        For example::

        >>> sessions = yield from client.sessions.dc('dc2').items()

        will fetch all sessions of ``dc2``.

        Parameters:
            name (str): datacenter name
        Returns:
            SessionEndpoint: a clone of this instance
        """
        instance = copy.copy(self)
        instance.dc = name
        return instance

    @asyncio.coroutine
    def create(self, *, name=None, node=None, checks=None,
               behavior=None, lock_delay=None, ttl=None):
        """Initialize a new session.

        A session can be invalidated if ttl is provided.

        Parameters:
            name (str): human-readable name for the session
            node (str): attach to this node, default to current agent
            checks (list): associate health checks
            behavior (str): controls the behavior when a session is invalidated
            lock_delay (int): duration of key lock.
            ttl (int): invalidated session until renew.
        Returns:
            Session: the fresh session
        """
        path = '/session/create'
        params = {'dc': self.dc}
        data = {}
        if lock_delay:
            data['LockDelay'] = format_duration(lock_delay)
        if node:
            data['Node'] = node
        if name:
            data['Name'] = extract_name(name)
        if checks:
            data['Checks'] = checks
        if behavior:
            data['Behavior'] = behavior
        if ttl is not None:
            data['TTL'] = format_duration(ttl)
        response = yield from self.client.put(path,
                                              params=params,
                                              data=json.dumps(data))
        if response.status == 200:
            return decode((yield from response.json()))

    @asyncio.coroutine
    def delete(self, session):
        """Delete session

        Parameters:
            session (Session): id of the session
        Returns:
            bool: True
        """
        path = '/session/destroy/%s' % extract_id(session)
        params = {'dc': self.dc}
        response = yield from self.client.put(path, params=params)
        return response.status == 200

    destroy = delete

    @asyncio.coroutine
    def get(self, session):
        """
        Returns the requested session information within datacenter.

        Parameters:
            session (Session): session id
        Returns:
            Session: queried session
        Raises:
            NotFound: session was not found
        """

        path = '/session/info/%s' % extract_id(session)
        params = {'dc': self.dc}
        response = yield from self.client.get(path, params=params)
        items = yield from response.json()
        for item in (items or []):
            return decode(item)
        raise self.NotFound('Session %r was not found' % extract_id(session))

    @asyncio.coroutine
    def items(self, *, node=None):
        """List active sessions.

        It will returns the active sessions for current datacenter.
        If node is specified, it will returns the active sessions for
        given node and current datacenter.

        Parameters:
            node (Node): filter this node
        Returns:
            DataSet: a set of :class:`~aioconsul.Session`
        """
        if node:
            path = '/session/node/%s' % extract_id(node)
        else:
            path = '/session/list'
        params = {'dc': self.dc}
        response = yield from self.client.get(path, params=params)
        values = {decode(item) for item in (yield from response.json())}
        return render(values, response=response)

    __call__ = items

    @asyncio.coroutine
    def renew(self, session):
        """
        If session was created with a TTL set, it will renew this session.

        Parameters:
            session (Session): the session
        Returns:
            bool: True
        """
        path = '/session/renew/%s' % extract_id(session)
        params = {'dc': self.dc}
        response = self.client.put(path, params=params)
        return response.status == 200


def decode(item):
    return Session(id=item.get('ID'),
                   behavior=item.get('Behavior'),
                   checks=item.get('Checks'),
                   create_index=item.get('CreateIndex'),
                   node=item.get('Node'))
