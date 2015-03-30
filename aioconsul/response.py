import json
from aioconsul.meta import ConsulMeta
from aioconsul.types import ConsulMapping, ConsulSet

__all__ = ['ConsulMeta', 'render']


def render(values, *, response):
    meta = json.loads(
        '{"last_index": %s, "last_contact": %s, "known_leader": %s}' % (
            response.headers.get('X-Consul-Index', 'null'),
            response.headers.get('X-Consul-LastContact', 'null'),
            response.headers.get('X-Consul-KnownLeader', 'null')
        )
    )

    if isinstance(values, dict):
        values = ConsulMapping(values)
    else:
        values = ConsulSet(values)
    values.consul = ConsulMeta(**meta)
    return values
