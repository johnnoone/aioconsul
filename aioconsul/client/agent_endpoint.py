from .bases import EndpointBase


class AgentEndpoint(EndpointBase):
    """Interact with the local Consul agent.
    """

    async def info(self):
        """Returns the local node configuration

        Returns:
            Object: local node configuration

        Returns the configuration and member information of the local agent
        under the Config key, like this::

            {
                "Config": {
                    "Bootstrap": True,
                    "Server": True,
                    "Datacenter": "dc1",
                    "DataDir": "/tmp/consul",
                    "DNSRecursor": "",
                    "DNSRecursors": [],
                    "Domain": "consul.",
                    "LogLevel": "INFO",
                    "NodeName": "foobar",
                    "ClientAddr": "127.0.0.1",
                    "BindAddr": "0.0.0.0",
                    "AdvertiseAddr": "10.1.10.12",
                    "Ports": {
                        "DNS": 8600,
                        "HTTP": 8500,
                        "RPC": 8400,
                        "SerfLan": 8301,
                        "SerfWan": 8302,
                        "Server": 8300
                    },
                    "LeaveOnTerm": False,
                    "SkipLeaveOnInt": False,
                    "StatsiteAddr": "",
                    "Protocol": 1,
                    "EnableDebug": False,
                    "VerifyIncoming": False,
                    "VerifyOutgoing": False,
                    "CAFile": "",
                    "CertFile": "",
                    "KeyFile": "",
                    "StartJoin": [],
                    "UiDir": "",
                    "PidFile": "",
                    "EnableSyslog": False,
                    "RejoinAfterLeave": False
                },
                "Coord": {
                    "Adjustment": 0,
                    "Error": 1.5,
                    "Vec": [0,0,0,0,0,0,0,0]
                },
                "Member": {
                    "Name": "foobar",
                    "Addr": "10.1.10.12",
                    "Port": 8301,
                    "Tags": {
                        "bootstrap": "1",
                        "dc": "dc1",
                        "port": "8300",
                        "role": "consul",
                        "vsn": "1",
                        "vsn_max": "1",
                        "vsn_min": "1"
                    },
                    "Status": 1,
                    "ProtocolMin": 1,
                    "ProtocolMax": 2,
                    "ProtocolCur": 2,
                    "DelegateMin": 2,
                    "DelegateMax": 4,
                    "DelegateCur": 4
                }
            }
        """
        response = await self._api.get("/v1/agent/self")
        return response.body

    async def disable(self, reason=None):
        """Enters maintenance mode

        Parameters:
            reason (str): Reason of disabling
        Returns:
            bool: ``True`` on success
        """
        params = {"enable": True, "reason": reason}
        response = await self._api.put("/v1/agent/maintenance", params=params)
        return response.status == 200

    async def enable(self, reason=None):
        """Resumes normal operation

        Parameters:
            reason (str): Reason of enabling
        Returns:
            bool: ``True`` on success
        """
        params = {"enable": False, "reason": reason}
        response = await self._api.put("/v1/agent/maintenance", params=params)
        return response.status == 200
