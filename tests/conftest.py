import asyncio
import json
import logging
import os
import os.path
import pytest
import sys
from aioconsul import Consul
from functools import wraps
from subprocess import Popen, PIPE
from time import sleep

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

HERE = os.path.dirname(os.path.abspath(__file__))


def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(pre_clean())
        loop.run_until_complete(future)
    return wrapper


@asyncio.coroutine
def pre_clean():
    client = Consul()

    # remove checks
    checks = yield from client.agent.checks()
    for check in checks:
        yield from client.agent.checks.delete(check)

    # remove services
    services = yield from client.agent.services()
    for service in services:
        if service.id != 'consul':
            yield from client.agent.services.delete(service)

    # remove keys
    for key in (yield from client.kv.keys('')):
        yield from client.kv.delete(key)

    # remove sessions
    sessions = yield from client.sessions()
    for session in sessions:
        yield from client.sessions.delete(session)


class Node(object):
    def __init__(self, name, config_file, server=False, leader=False):
        self.name = name
        self.config_file = config_file
        self.server = server
        self.leader = leader
        self._proc = None

    @property
    def config(self):
        with open(self.config_file) as file:
            return json.load(file)

    def start(self):
        if self._proc:
            raise Exception('Node %s is already running' % self.name)

        # reset tmp store
        Popen(['rm', '-rf', self.config['data_dir']]).communicate()

        env = os.environ.copy()
        env.setdefault('GOMAXPROCS', '2')
        proc = Popen(['consul', 'agent', '-config-file=%s' % self.config_file],
                     stdout=PIPE, stderr=PIPE, env=env, shell=False)
        self._proc = proc
        print('Starting %s [%s]' % (self.name, proc.pid))
        for i in range(60):
            with Popen(['consul', 'info'], stdout=PIPE, stderr=PIPE) as sub:
                stdout, stderr = sub.communicate(timeout=5)
                if self.leader:
                    if 'leader = true' in stdout.decode('utf-8'):
                        break
                elif self.server:
                    if 'server = true' in stdout.decode('utf-8'):
                        break
                elif not sub.returncode:
                    break
            sleep(1)
        else:
            raise Exception('Unable to start %s [%s]' % (self.name, proc.pid))
        print('Node %s [%s] is ready to rock' % (self.name, proc.pid))

    def stop(self):
        if not self._proc:
            raise Exception('Node %s is not running' % self.name)
        print('Halt %s [%s]' % (self.name, self._proc.pid))
        result = self._proc.terminate()
        self._proc = None
        return result


@pytest.fixture(scope="session", autouse=True)
def leader(request):
    config_file = os.path.join(HERE, 'consul-server.json')
    node = Node('leader', config_file, True, True)
    node.start()
    request.addfinalizer(node.stop)
    return node.config


@pytest.fixture(scope="session", autouse=False)
def node1(request):
    config_file = os.path.join(HERE, 'consul-node.json')
    node = Node('leader', config_file, False, False)
    node.start()
    request.addfinalizer(node.stop)
    return node.config
