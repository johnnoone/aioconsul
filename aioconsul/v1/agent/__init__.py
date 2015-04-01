import asyncio
import logging
from aioconsul.bases import Config, Member
from aioconsul.util import extract_name, task
from .check import AgentCheckEndpoint
from .service import AgentServiceEndpoint

logger = logging.getLogger(__name__)


class AgentEndpoint:

    def __init__(self, client, *, loop=None):
        self.client = client
        self.checks = AgentCheckEndpoint(client)
        self.services = AgentServiceEndpoint(client)
        self.loop = loop or asyncio.get_event_loop()

    @task
    def members(self):
        """Returns a set of members.

        Returns:
            set: set of :class:`Member` instances
        """
        response = yield from self.client.get('/agent/members')
        return {decode_member(item) for item in (yield from response.json())}

    @task
    def config(self):
        """Returns configuration of agent.

        Returns:
            Config: instance

        """
        response = yield from self.client.get('/agent/self')
        data = yield from response.json()
        return decode_config(data['Config'])

    @task
    def me(self):
        """Returns the member object of agent.

        Returns:
            Member: instance

        """
        response = yield from self.client.get('/agent/self')
        data = yield from response.json()
        return decode_member(data['Member'])

    @task
    def enable(self, reason=None):
        """Enable agent.

        Parameters:
            reason (str): human readable reason
        Returns:
             bool: ``True`` it has been enabled
        """
        params = {
            'enable': False,
            'reason': reason
        }
        response = yield from self.client.put('/agent/maintenance',
                                              params=params)
        return response.status == 200

    @task
    def disable(self, reason=None):
        """Disable agent.

        Parameters:
            reason (str): human readable reason
        Returns:
             bool: ``True`` it has been disabled
        """
        params = {
            'enable': True,
            'reason': reason
        }
        response = yield from self.client.put('/agent/maintenance',
                                              params=params)
        return response.status == 200

    @task
    def join(self, address, *, wan=None):
        """Asks the agent to join a cluster.

        Parameters:
            address (str): address to join
            wan (str): use wan?
        Returns:
            bool: agent status
        """
        path = '/agent/join/%s' % str(address).lstrip('/')
        params = {}
        if wan:
            params['wan'] = 1
        response = yield from self.client.get(path, params=params)
        return response.status == 200

    @task
    def force_leave(self, member):
        """Asks a member to leave the cluster.

        Parameters:
            member (Member): member or name
        Returns:
            bool: action status
        """
        path = '/agent/force-leave/%s' % extract_name(member)
        response = yield from self.client.get(path)
        return response.status == 200


def decode_config(data):
    ports = data.get('Ports', {})
    return Config(bootstrap=data.get('Bootstrap'),
                  server=data.get('Server'),
                  datacenter=data.get('Datacenter'),
                  data_dir=data.get('DataDir'),
                  dns_recursor=data.get('DNSRecursor'),
                  dns_recursors=data.get('DNSRecursors'),
                  domain=data.get('Domain'),
                  log_level=data.get('LogLevel'),
                  node_name=data.get('NodeName'),
                  client_address=data.get('ClientAddr'),
                  bind_address=data.get('BindAddr'),
                  advertise_address=data.get('AdvertiseAddr'),
                  port=dict(dns=ports.get('DNS'),
                            http=ports.get('HTTP'),
                            rpc=ports.get('RPC'),
                            serf_lan=ports.get('SerfLan'),
                            serf_wan=ports.get('SerfWan'),
                            server=ports.get('Server')),
                  leave_on_term=data.get('LeaveOnTerm'),
                  skip_leave_on_int=data.get('SkipLeaveOnInt'),
                  statsite_address=data.get('StatsiteAddr'),
                  protocol=data.get('Protocol'),
                  enable_debug=data.get('EnableDebug'),
                  verify_incoming=data.get('VerifyIncoming'),
                  verify_outgoing=data.get('VerifyOutgoing'),
                  ca_file=data.get('CAFile'),
                  cert_file=data.get('CertFile'),
                  key_file=data.get('KeyFile'),
                  start_join=data.get('StartJoin'),
                  ui_dir=data.get('UiDir'),
                  pid_file=data.get('PidFile'),
                  enable_syslog=data.get('EnableSyslog'),
                  rejoin_after_leave=data.get('RejoinAfterLeave'))


def decode_member(data):
    return Member(name=data.get('Name'),
                  address=data.get('Addr'),
                  port=data.get('Port'),
                  status=data.get('Status'),
                  tags=data.get('Tags'),
                  delegate_cur=data.get('DelegateCur'),
                  delegate_max=data.get('DelegateMax'),
                  delegate_min=data.get('DelegateMin'),
                  protocol_cur=data.get('ProtocolCur'),
                  protocol_max=data.get('ProtocolMax'),
                  protocol_min=data.get('ProtocolMin'))
