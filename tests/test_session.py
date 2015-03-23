import pytest
from aioconsul import Consul
from conftest import async_test


@async_test
def test_sessions():
    client = Consul()

    # create a session
    session1 = yield from client.session.create()
    assert hasattr(session1, 'id')

    # fetch data of this session
    session2 = yield from client.session.get(session1)
    assert hasattr(session2, 'id')
    assert session1 == session2

    # fetch all sessions
    sessions_a = yield from client.session.items()
    assert len(sessions_a) == 1
    assert session2 in sessions_a

    # fetch all sessions from my node (they shoul be the same than above)
    sessions_b = yield from client.session.items(node='my-local-node')
    assert len(sessions_b) == 1
    assert session2 in sessions_b
    assert sessions_a == sessions_b

    # delete the session
    session_id = session1.id
    deleted = yield from client.session.delete(session_id)
    assert deleted

    # try to refetch the session
    with pytest.raises(client.session.NotFound):
        session3 = yield from client.session.get(session_id)
