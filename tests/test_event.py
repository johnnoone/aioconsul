import asyncio
import pytest
from aioconsul import Consul, ValidationError
from conftest import async_test


@async_test
def test_event():
    client = Consul()

    tasks = [
        asyncio.async(client.events.fire('my-event-a', 'my-payload')),
        asyncio.async(client.events.fire('my-event-b', 'my-payload')),
        asyncio.async(client.events.fire('my-event-c', 'my-payload', node_filter='that-s-not-my-name')),
        asyncio.async(client.events.fire('my-event-d', 'my-payload', service_filter='that-s-not-my-name')),
        asyncio.async(client.events.fire('my-event-e', 'my-payload', service_filter='that-s-not-my-name', tag_filter='loled')),
    ]

    done, pending = yield from asyncio.wait(tasks)
    events = {fut.result() for fut in done}
    assert len(events) == 5
    event_a, event_b, event_c, event_d, event_e = sorted(events, key=lambda x: x.name)

    tasks = [
        asyncio.async(client.events()),
        asyncio.async(client.events(event='my-event-a')),
        asyncio.async(client.events(event='my-event-b')),
        asyncio.async(client.events(event='my-event-c')),
        asyncio.async(client.events(event='my-event-d')),
        asyncio.async(client.events(event='my-event-e')),
    ]

    done, pending = yield from asyncio.wait(tasks)
    eventsets = [fut.result() for fut in done]
    a, b, c, d, e = 0, 0, 0, 0, 0
    for events in eventsets:
        if event_a in events:
            a = a + 1
        if event_b in events:
            b = b + 1
        if event_c in events:
            c = c + 1
        if event_d in events:
            d = d + 1
        if event_e in events:
            e = e + 1

    assert (a, b, c, d, e) == (2, 2, 0, 0, 0)

    with pytest.raises(ValidationError):
        yield from client.events.fire('my-event-f', 'my-payload', tag_filter='sparta')
