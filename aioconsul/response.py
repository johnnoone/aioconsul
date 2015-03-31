import json
from aioconsul.meta import ConsulMeta
from aioconsul.types import ConsulMapping, ConsulSet

__all__ = ['render', 'render_meta']


def render(values, *, response=None):
    if isinstance(values, dict):
        values = ConsulMapping(values)
    else:
        values = ConsulSet(values)
    if response:
        values.consul = render_meta(response)
    return values


def render_meta(response):
    params = json.loads(
        '{"last_index": %s, "last_contact": %s, "known_leader": %s}' % (
            response.headers.get('X-Consul-Index', 'null'),
            response.headers.get('X-Consul-LastContact', 'null'),
            response.headers.get('X-Consul-KnownLeader', 'null')
        )
    )
    return ConsulMeta(**params)
