import asyncio
import logging
from aioconsul.bases import Member
from .check import AgentCheckEndpoint
from .service import AgentServiceEndpoint

logger = logging.getLogger(__name__)


class AgentEndpoint:

    def __init__(self, client):
        self.client = client
        self.checks = AgentCheckEndpoint(client)
        self.services = AgentServiceEndpoint(client)

    @asyncio.coroutine
    def members(self):
        """Returns a set of members.

        Returns:
            set: a set of members
        """
        response = yield from self.client.get('/agent/members')
        return [decode_member(item) for item in (yield from response.json())]

    @asyncio.coroutine
    def me(self):
        """Returns info about current agent.

        Returns:
            dict: information mapping

        """
        response = yield from self.client.get('/agent/self')
        data = yield from response.json()
        if 'Member' in data:
            data['Member'] = decode_member(data['Member'])
        return data

    @asyncio.coroutine
    def maintenance(self, enable, reason=None):
        """Switch agent maintenance mode.

        Parameters:
            enable (bool): Should we put this agent in maintenance mode?
            reason (str): An opaque str about the maintenance.

        Returns:
            bool: Agent status
        """
        params = {
            'enable': enable,
            'reason': reason
        }
        response = yield from self.client.put('/agent/maintenance',
                                              params=params)
        return response.status == 200

    @asyncio.coroutine
    def join(self, address, *, wan=None):
        """Asks the agent to join a cluster.

        Parameters:
            address (str): Address to join
            wan (str): Use wan?

        Returns:
            bool: Agent status
        """
        path = '/agent/join/%s' % str(address).lstrip('/')
        params = {}
        if wan:
            params['wan'] = 1
        response = yield from self.client.get(path, params=params)
        return response.status == 200

    @asyncio.coroutine
    def force_leave(self, member):
        """Asks a member to leaver the cluster.

        Parameters:
            member (str): The member to remove from cluster.

        Returns:
            bool: Action status
        """
        path = '/agent/force-leave/%s' % extract_name(member)
        response = yield from self.client.get(path)
        return response.status == 200


def decode_member(data):
    return Member(address=data.get('Addr'),
                  name=data.get('Name'),
                  port=data.get('Port'),
                  status=data.get('Status'),
                  tags=data.get('Tags'),
                  delegate_cur=data.get('DelegateCur'),
                  delegate_max=data.get('DelegateMax'),
                  delegate_min=data.get('DelegateMin'),
                  protocol_cur=data.get('ProtocolCur'),
                  protocol_max=data.get('ProtocolMax'),
                  protocol_min=data.get('ProtocolMin'))
