import json
import os
import pytest
import subprocess
import time
from aioconsul import Consul
from tempfile import NamedTemporaryFile
from uuid import uuid4


def run(cmd, **kwargs):
    kwargs.setdefault("stdout", subprocess.PIPE)
    kwargs.setdefault("stderr", subprocess.PIPE)
    return subprocess.Popen(cmd, **kwargs)


class Namespace:

    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)


@pytest.fixture(scope="session")
def master_token():
    return uuid4().__str__()


@pytest.fixture(scope="session")
def server(master_token):
    conf = {
          "node_name": "server1",
          "server": True,
          "acl_datacenter": "dc1",
          "acl_master_token": master_token
    }

    with NamedTemporaryFile(mode="w+") as file:
        json.dump(conf, file)
        file.seek(0)

        env = os.environ.copy()
        env.setdefault('GOMAXPROCS', '4')
        bin = env.get("CONSUL_BIN", "consul")

        proc = run([bin, "agent", "-dev", "-config-file", file.name], env=env)

        buf = bytearray()
        while b"cluster leadership acquired" not in buf:
            buf = proc.stdout.readline()
            time.sleep(.01)
            if proc.returncode is not None:
                raise Exception("Server failed to start")

        yield Namespace(address="http://127.0.0.1:8500",
                        name="server1",
                        dc="dc1",
                        token=master_token, **conf)
        proc.terminate()


@pytest.fixture(scope="function")
def client(server, event_loop):
    consul = Consul(server.address, token=server.token, loop=event_loop)
    yield consul

    # handle some cleanup
    async def cleanup(consul):
        keys, meta = await consul.kv.keys("")
        for key in keys:
            await consul.kv.delete(key)
        await consul.catalog.deregister({
            "Node": "foobar"
        })

    event_loop.run_until_complete(cleanup(consul))
