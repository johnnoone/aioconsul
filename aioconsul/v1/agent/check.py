import asyncio
import json
from aioconsul.bases import Check
from aioconsul.util import extract_id, format_duration


class AgentCheckEndpoint:

    class NotFound(ValueError):
        """Raised when check was not found"""

    def __init__(self, client):
        self.client = client

    @asyncio.coroutine
    def items(self):
        """Returns the checks the local agent is managing.

        Returns:
            set: set of :class:`Check` instances
        """
        response = yield from self.client.get('/agent/checks')
        items = yield from response.json()
        return {decode(item) for item in items.values()}

    __call__ = items

    @asyncio.coroutine
    def register_script(self, name, script, *, interval, id=None, notes=None):
        """Registers a new local check by script.

        Parameters:
            name (str): check name
            script (str): path to script
            interval (str): evaluate script every `ìnterval`
            id (str): check id
            notes (str): human readable notes
        Returns:
             Check: instance
        """
        response = yield from self.register(id=id,
                                            name=name,
                                            notes=notes,
                                            interval=interval,
                                            script=script)
        return response

    @asyncio.coroutine
    def register_http(self, name, http, *, interval, id=None, notes=None):
        """Registers a new local check by http.

        Parameters:
            name (str): check name
            http (str): url to ping
            interval (str): evaluate script every `ìnterval`
            id (str): check id
            notes (str): human readable notes
        Returns:
             Check: instance
        """
        response = yield from self.register(id=id,
                                            name=name,
                                            notes=notes,
                                            interval=interval,
                                            http=http)
        return response

    @asyncio.coroutine
    def register_ttl(self, name, ttl, *, id=None, notes=None):
        """Registers a new local check by ttl.

        Parameters:
            name (str): check name
            ttl (str): period status update
            id (str): check id
            notes (str): human readable notes
        Returns:
             Check: instance
        """
        response = yield from self.register(id=id,
                                            name=name,
                                            notes=notes,
                                            ttl=ttl)
        return response

    @asyncio.coroutine
    def register(self, name, **params):
        """Registers a new local check.

        Parameters:
            name (str): check name
            http (str): url to ping
            script (str): path to script
            ttl (str): period status update
            interval (str): evaluate script every `ìnterval`
            id (str): check id
            notes (str): human readable notes
        Returns:
             Check: instance
        """
        path = '/agent/check/register'
        data = {
            'Name': name,
            'ID': params.get('id'),
            'Notes': params.get('notes'),
            'HTTP': params.get('http'),
            'Script': params.get('script'),
            'TTL': params.get('ttl'),
            'Interval': params.get('interval')
        }
        data = {k: v for k, v in data.items() if v is not None}
        if 'TTL' in data:
            data['TTL'] = format_duration(data['TTL'])
        if 'Interval' in data:
            data['Interval'] = format_duration(data['Interval'])

        response = yield from self.client.put(path, data=json.dumps(data))
        if response.status == 200:
            return Check(id=params.get('id', name), name=name)

    @asyncio.coroutine
    def deregister(self, check):
        """Deregisters a local check.

        Parameters:
            check (Check): check or id
        Returns:
            bool: ``True`` check has been deregistered
        """
        path = '/agent/check/deregister/%s' % extract_id(check)
        response = yield from self.client.get(path)
        return response.status == 200

    @asyncio.coroutine
    def passing(self, check, note=None):
        """Marks a local test as passing.

        Parameters:
            check (Check): check or id
            note (str): human readable reason
        Returns:
            bool: ``True`` check has been deregistered
        """
        response = yield from self.mark(check, 'passing', note=note)
        return response

    @asyncio.coroutine
    def warning(self, check, note=None):
        """Marks a local test as warning.

        Parameters:
            check (Check): check or id
            note (str): human readable reason
        Returns:
            bool: ``True`` check has been deregistered
        """
        response = yield from self.mark(check, 'warning', note=note)
        return response

    @asyncio.coroutine
    def failing(self, check, note=None):
        """Marks a local test as critical.

        Parameters:
            check (Check): check or id
            note (str): human readable reason
        Returns:
            bool: ``True`` check has been deregistered
        """
        response = yield from self.mark(check, 'critical', note=note)
        return response

    critical = failing

    @asyncio.coroutine
    def mark(self, check, state, *, note=None):
        """Set state of a local test.

        Parameters:
            check (Check): check or id
            state (str): ``passing``, ``warning`` or ``failing``
            note (str): human readable reason
        Returns:
            bool: ``True`` check has been deregistered
        """
        route = {'passing': 'pass',
                 'warning': 'warn',
                 'failing': 'fail',
                 'critical': 'fail'}.get(state, state)
        path = '/agent/check/%s/%s' % (route, extract_id(check))
        response = yield from self.client.get(path, params={'note': note})
        return response.status == 200

    @asyncio.coroutine
    def get(self, check):
        """Get a local test.

        Parameters:
            check (Check): check or id
        Returns:
            Check: instance
        Raises:
            NotFound: check was not found
        """
        response = yield from self.client.get('/agent/checks')
        items = yield from response.json()
        check_id = extract_id(check)
        try:
            return decode(items[check_id])
        except KeyError:
            raise self.NotFound('Check %r was not found' % check_id)

    create = register
    delete = deregister


def decode(data):
    return Check(id=data.get('CheckID'),
                 name=data.get('Name'),
                 status=data.get('Status'),
                 notes=data.get('Notes'),
                 output=data.get('Output'),
                 service_id=data.get('ServiceID'),
                 service_name=data.get('ServiceName'),
                 node=data.get('Node'))
