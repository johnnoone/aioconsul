import asyncio
import json
import logging
from collections import defaultdict
from aioconsul.bases import ACL, Rule
from aioconsul.exceptions import ACLSupportDisabled, HTTPError
from aioconsul.request import RequestWrapper
from aioconsul.util import extract_id

logger = logging.getLogger(__name__)


class SupportedClient(RequestWrapper):
    """
    Supported Client

    It can handle ACL request with barrier. See :py:class:`ACLEndpoint`
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

    :ivar supported: Used as a barrier, it will be defined at the first
                     request. Set it to ``None`` for resetting.
    """

    class NotFound(ValueError):
        """Raises when an ACL was not found."""
        pass

    def __init__(self, client, supported=None):
        self.supported = supported
        self.client = SupportedClient(client, self)

    @asyncio.coroutine
    def is_supported(self):
        """Tells if ACL is supported or not.

        :returns: yes or no
        :rtype: bool
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
    def create(self, acl, *, type=None, rules=None):
        """Create an ACL

        :param acl: the futur name of the ACL
        :type acl: :py:class:`ACL` or str
        :param type: the type of the :py:class:`ACL` (client or management)
        :type type: str
        :param rules: A set of rules to implement. These rules can
                      be a list of :py:class:`Rule` instances,
                      or 3 length tuples.
        :type rules: set
        :returns: the new acl id that can be used as a token for
                  :py:class:`Consul` instances.
        :rtype: str
        """
        path = 'acl/create'
        name = getattr(acl, 'name', acl)
        type = type or 'client'
        data = {
            'Name': name,
            'Type': type,
            'Rules': encode_rules(rules)
        }
        response = yield from self.client.put(path, data=json.dumps(data))
        return (yield from response.json())['ID']

    @asyncio.coroutine
    def update(self, acl, *, name=None, type=None, rules=None):
        """Update an ACL

        :param acl: the ACL id to update
        :type acl: :py:class:`ACL` or str
        :param name: the new name of acl
        :type name: str
        :param type: the new type of the :py:class:`ACL` (client or management)
        :type type: str
        :param rules: A set of new rules to implement. These rules can
                      be a list of :py:class:`Rule` instances,
                      or 3 length tuples.
        :type rules: set
        :returns: the acl id that can be used as a token for
                  :py:class:`Consul` instances.
        :rtype: str
        """
        path = 'acl/update'
        data = {
            'ID': extract_id(acl),
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
    def destroy(self, acl):
        """Destroy an ACL

        :param acl: the ACL id to update
        :type acl: :py:class:`ACL` or str
        :returns: yes or no if it was destroyed
        :rtype: bool
        """
        path = 'acl/destroy/%s' % extract_id(acl)
        response = yield from self.client.put(path)
        return response.status == 200

    @asyncio.coroutine
    def get(self, acl):
        """Destroy an ACL

        :param acl: the ACL id to update
        :type acl: :py:class:`ACL` or str
        :returns: The ACL instance
        :rtype: :py:class:`ACL`
        """
        path = 'acl/info/%s' % extract_id(acl)
        response = yield from self.client.get(path)
        for data in (yield from response.json()) or []:
            return decode(data)
        else:
            raise self.NotFound('ACL %s was not found' % acl)

    @asyncio.coroutine
    def clone(self, acl):
        """Clone an ACL

        :param acl: the ACL id to update
        :type acl: :py:class:`ACL` or str
        :returns: The id of the new ACL clone
        :rtype: str
        """
        path = 'acl/info/%s' % extract_id(acl)
        response = yield from self.client.put(path)
        return (yield from response.json())['ID']

    @asyncio.coroutine
    def items(self):
        """Returns a set of all ACL.

        :returns: A set of ACL instances
        :rtype: set
        """
        path = 'acl/list'
        response = yield from self.client.get(path)
        return [decode(data) for data in (yield from response.json())]

    delete = destroy


def decode(data):
    return ACL(id=data.get('ID'),
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