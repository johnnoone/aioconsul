import asyncio
import json
import logging
from collections import defaultdict
from aioconsul.bases import Token, Rule
from aioconsul.exceptions import ACLSupportDisabled
from aioconsul.request import RequestWrapper
from aioconsul.response import render
from aioconsul.util import extract_id

logger = logging.getLogger(__name__)


class SupportedClient(RequestWrapper):
    """
    Supported Client

    It can handle ACL request with barrier. See :py:class:`ACLEndpoint`.
    """

    def __init__(self, client, obj):
        self.client = client
        self.obj = obj

    @asyncio.coroutine
    def request(self, method, path, **kwargs):
        if self.obj.supported is False:
            raise ACLSupportDisabled()

        response = yield from self.client.request(method, path, **kwargs)
        if response.status in (401, 403):
            if self.obj.supported is None:
                self.obj.supported = False
            body = yield from response.text()
            raise ACLSupportDisabled(body)
        self.obj.supported = True
        return response


class ACLEndpoint:
    """
    ACL Endpoint

    Attributes:
        supported (bool): Used as a barrier, it will be defined at the
                          first request. Set it to ``None`` for resetting.
    """

    class NotFound(ValueError):
        """Raises when a token was not found."""
        pass

    def __init__(self, client, *, loop=None, supported=None):
        self.supported = supported
        self.client = SupportedClient(client, self)
        self.loop = loop or asyncio.get_event_loop()

    @asyncio.coroutine
    def is_supported(self):
        """Tells if ACL is supported or not.

        Returns:
            bool: yes or no
        """
        if self.supported is None:
            try:
                yield from self.client.get('acl/list')
            except ACLSupportDisabled:
                supported = False
            else:
                supported = True
            self.supported = supported
        return self.supported

    @asyncio.coroutine
    def create(self, name, *, type=None, rules=None, obj=False):
        """Create a new token.

        A :class:`Token` has a name, a type, and a set of ACL rules.

        The result can be used as a token into :py:class:`Consul` instances.

        Parameters:
            name (str): human name
            type (str): ``client`` or ``management``
            rules (list): a set of rules to implement, which can be a list of
                          :py:class:`Rule` instances or 3 length tuples.
            obj (bool): must returns a :class:`Token` instance
                        at the cost of additional http queries.
        Returns:
            str | Token: id or :class:`Token`, depending of `obj` parameter.
        """
        path = 'acl/create'
        data = {
            'Name': name,
            'Type': type or 'client',
            'Rules': encode_rules(rules)
        }
        response = yield from self.client.put(path, data=json.dumps(data))
        return (yield from self._parse_put_token(response, obj))

    @asyncio.coroutine
    def update(self, token, *, name=None, type=None, rules=None, obj=False):
        """Update a token.

        The result can be used as a token into :py:class:`Consul` instances.

        Parameters:
            token (Token): token or id to update
            name (Token): human name
            type (str): ``client`` or ``management``
            rules (list): a set of rules to implement, which can be a list of
                          :py:class:`Rule` instances or 3 length tuples.
            obj (bool): must returns a :class:`Token` instance
                        at the cost of additional http queries.
        Returns:
            str | Token: id or :class:`Token`, depending of `obj` parameter.
        """
        path = 'acl/update'
        data = {
            'ID': extract_id(token),
        }
        if name is not None:
            data['Name'] = name
        if type is not None:
            data['Type'] = type
        if rules is not None:
            data['Rules'] = encode_rules(rules)
        response = yield from self.client.put(path, data=json.dumps(data))
        return (yield from self._parse_put_token(response, obj))

    @asyncio.coroutine
    def destroy(self, token):
        """Destroy a token.

        Parameters:
            token (Token): token or id to delete
        Returns:
            bool: ``True``, it was destroyed
        """
        path = 'acl/destroy/%s' % extract_id(token)
        response = yield from self.client.put(path)
        return (yield from response.json())

    delete = destroy

    @asyncio.coroutine
    def get(self, token):
        """Get a token.

        The result can be used as a token into :py:class:`Consul` instances.

        Parameters:
            token (Token): token or id
        Returns:
            Token: token instance
        Raises:
            NotFound: token was not found
        """
        path = 'acl/info/%s' % extract_id(token)
        response = yield from self.client.get(path)
        for data in (yield from response.json()) or []:
            return decode(data)
        else:
            raise self.NotFound('Token %s was not found' % token)

    @asyncio.coroutine
    def clone(self, token, *, obj=False):
        """Clone a token.

        The result can be used as a token into :py:class:`Consul` instances.

        Parameters:
            token (Token): token or id to clone
            obj (bool): must returns a :class:`Token` instance
                        at the cost of additional http queries.
        Returns:
            str | Token: id or :class:`Token`, depending of `obj` parameter.
        """
        path = 'acl/clone/%s' % extract_id(token)
        response = yield from self.client.put(path)
        return (yield from self._parse_put_token(response, obj))

    @asyncio.coroutine
    def _parse_put_token(self, response, obj=False):
        """Parse a response, and fetch object, or not!

        Internal purpose only"""
        token_id = (yield from response.json())['ID']
        if obj:
            return (yield from self.get(token_id))
        else:
            return token_id

    @asyncio.coroutine
    def items(self):
        """Returns a set of all Token.

        Returns:
            ConsulSet: set of :class:`Token` instances
        """
        path = 'acl/list'
        response = yield from self.client.get(path)
        values = {decode(data) for data in (yield from response.json())}
        return render(values, response=response)

    __call__ = items


def decode(data):
    return Token(id=data.get('ID'),
                 name=data.get('Name'),
                 type=data.get('Type'),
                 rules=decode_rules(data.get('Rules')),
                 create_index=data.get('CreateIndex'),
                 modify_index=data.get('ModifyIndex'))


def decode_rules(data):
    if data and isinstance(data, str):
        data = json.loads(data)
    data, rules = data or {}, []
    for type, members in data.items():
        for value, info in members.items():
            rules.append(Rule(type, value, info['policy']))
    return rules


def encode_rules(rules):
    data, rules = defaultdict(dict), rules or []
    for type, value, policy in rules:
        policy = {'allow': 'write',
                  True: 'write',
                  False: 'deny'}.get(policy, policy)
        data[type][value] = {'policy': policy}
    return json.dumps(data)
