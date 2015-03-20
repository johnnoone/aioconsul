import asyncio
import json
import logging
from collections import defaultdict
from aioconsul.bases import Token, Rule
from aioconsul.exceptions import ACLSupportDisabled, HTTPError
from aioconsul.request import RequestWrapper
from aioconsul.util import extract_id, extract_name

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

        try:
            response = yield from self.client.request(method, path, **kwargs)
            self.obj.supported = True
            return response
        except HTTPError as error:
            if error.status in (401, 403):
                if self.obj.supported is None:
                    self.obj.supported = False
                raise ACLSupportDisabled(str(error))
            raise


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

    def __init__(self, client, supported=None):
        self.supported = supported
        self.client = SupportedClient(client, self)

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
    def create(self, token, *, type=None, rules=None):
        """Create a token.

        It is used to make a new token.
        A token has a name, a type, and a set of ACL rules.

        The result is a token id that can be used as a token into
        :py:class:`Consul` instances

        Parameters:
            token (Token): the futur name of the Token
            type (str): the type of the :py:class:`Token` (client or
                        management)
            rules (list): A set of rules to implement. These rules can be a
                          list of :py:class:`Rule` instances, or 3 length
                          tuples.

        Returns:
            str: token id
        """
        path = 'acl/create'
        name = extract_name(token)
        type = type or 'client'
        data = {
            'Name': name,
            'Type': type,
            'Rules': encode_rules(rules)
        }
        response = yield from self.client.put(path, data=json.dumps(data))
        return (yield from response.json())['ID']

    @asyncio.coroutine
    def update(self, token, *, name=None, type=None, rules=None):
        """Update a token

        The result is a token id that can be used as a token into
        :py:class:`Consul` instances

        Parameters:
            token (Token): the Token id to update
            name (str): the new name of token
            type (str): the new type (client or management)
            rules (list): A set of new rules to implement. These rules can
                          be a list of :py:class:`Rule` instances,
                          or 3 length tuples.

        Returns:
            str: token id

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
        return (yield from response.json())['ID']

    @asyncio.coroutine
    def destroy(self, token):
        """Destroy a token

        Parameters:
            token (Token): the Token id to update
        Returns:
            bool: yes or no if it was destroyed
        """
        path = 'acl/destroy/%s' % extract_id(token)
        response = yield from self.client.put(path)
        return response.status == 200

    @asyncio.coroutine
    def get(self, token):
        """Destroy a token

        Parameters:
            token (Token): the Token id to update
        Returns:
            Token: The Token instance
        """
        path = 'acl/info/%s' % extract_id(token)
        response = yield from self.client.get(path)
        for data in (yield from response.json()) or []:
            return decode(data)
        else:
            raise self.NotFound('Token %s was not found' % token)

    @asyncio.coroutine
    def clone(self, token):
        """Clone a token

        Parameters:
            acl (Token): the Token id to update
        Returns:
            str: The id of the new Token clone
        """
        path = 'acl/info/%s' % extract_id(token)
        response = yield from self.client.put(path)
        return (yield from response.json())['ID']

    @asyncio.coroutine
    def items(self):
        """Returns a set of all Token.

        Returns:
            set: A set of :class:`Token` instances
        """
        path = 'acl/list'
        response = yield from self.client.get(path)
        return [decode(data) for data in (yield from response.json())]

    delete = destroy


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
