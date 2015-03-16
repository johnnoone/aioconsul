import asyncio
import logging
from aioconsul import Consul
from functools import wraps

logger = logging.getLogger(__name__)


def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


@async_test
def test_sessions():
    client = Consul()

    sessions = yield from client.sessions.items()
    for session in sessions:
        logger.info('destroy previous session %s', session)
        yield from client.sessions.delete(session)

    # create a session
    session1 = yield from client.sessions.create()
    assert hasattr(session1, 'id')

    # fetch data of this session
    session2 = yield from client.sessions.get(session1)
    assert hasattr(session2, 'id')
    assert session1.id == session2.id

    # fetch all sessions
    sessions_a = yield from client.sessions.items()
    assert len(sessions_a) == 1
    assert session2 == sessions_a[0]

    # fetch all sessions from my node (they shoul be the same than above)
    sessions_b = yield from client.sessions.node('my-local-node')
    assert len(sessions_b) == 1
    assert session2 == sessions_b[0]
    assert sessions_a == sessions_b

    # delete the session
    session_id = session1.id
    deleted = yield from client.sessions.delete(session_id)
    assert deleted

    # try to refetch the session
    try:
        session3 = yield from client.sessions.get(session_id)
    except client.sessions.NotFound:
        assert True
    else:
        assert False, session3
