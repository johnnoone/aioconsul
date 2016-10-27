Raw API
=======

.. currentmodule:: aioconsul.api

This is a low-level wrapper of Consul_ HTTP API, intended to be the most
simple.



.. autoclass:: aioconsul.api.API
    :no-members:
    :no-undoc-members:
    :no-inherited-members:

    .. attribute:: token

          str – Token ID

    .. attribute:: address

          Address of agent. It can be provided in one of these form::

              ":port"
              "domain:port"
              ("domain", port)

    .. attribute:: consistency

        Most of the read query endpoints support multiple levels of consistency.
        Since no policy will suit all clients' needs, these consistency modes
        allow the user to have the ultimate say in how to balance the trade-offs
        inherent in a distributed system. The three read modes are:

        **default** — If not specified, the default is strongly consistent in
        almost all cases. However, there is a small window in which a new leader
        may be elected during which the old leader may service stale values. The
        trade-off is fast reads but potentially stale values. The condition
        resulting in stale reads is hard to trigger, and most clients should not
        need to worry about this case. Also, note that this race condition only
        applies to reads, not writes.

        **consistent** — This mode is strongly consistent without caveats.
        It requires that a leader verify with a quorum of peers that it is still
        leader. This introduces an additional round-trip to all server nodes.
        The trade-off is increased latency due to an extra round trip. Most
        clients should not use this unless they cannot tolerate a stale read.

        **stale** — This mode allows any server to service the read regardless
        of whether it is the leader. This means reads can be arbitrarily stale;
        however, results are generally consistent to within 50 milliseconds of
        the leader. The trade-off is very fast and scalable reads with a higher
        likelihood of stale values. Since this mode allows reads without a
        leader, a cluster that is unavailable will still be able to respond to
        queries.

    .. comethod:: get(*path, params, headers, body, json)

        Performs a GET request

        :param path: parts of path
        :type path: List[str]
        :param params: get parameters
        :type params: Dict[str, Any]
        :param headers: HTTP headers
        :type headers: Dict[str, str]
        :param body: content body
        :type body: bytes
        :param json: json body
        :type json: object
        :rtype: Response

    .. comethod:: post(*path, params, headers, body, json)

        Performs a POST request

        :param path: parts of path
        :type path: List[str]
        :param params: get parameters
        :type params: Dict[str, Any]
        :param headers: HTTP headers
        :type headers: Dict[str, str]
        :param body: content body
        :type body: bytes
        :param json: json body
        :type json: object
        :rtype: Response

    .. comethod:: put(*path, params, headers, body, json)

        Performs a PUT request

        :param path: parts of path
        :type path: List[str]
        :param params: get parameters
        :type params: Dict[str, Any]
        :param headers: HTTP headers
        :type headers: Dict[str, str]
        :param body: content body
        :type body: bytes
        :param json: json body
        :type json: object
        :rtype: Response

    .. comethod:: delete(*path, params, headers, body, json)

        Performs a DELETE request

        :param path: parts of path
        :type path: List[str]
        :param params: get parameters
        :type params: Dict[str, Any]
        :param headers: HTTP headers
        :type headers: Dict[str, str]
        :param body: content body
        :type body: bytes
        :param json: json body
        :type json: object
        :rtype: Response

    .. comethod:: request(method, *path, params, headers, body, json)

        Performs a request to path

        :param method: request's method
        :type method: str
        :param path: parts of path
        :type path: List[str]
        :param params: get parameters
        :type params: Dict[str, Any]
        :param headers: HTTP headers
        :type headers: Dict[str, str]
        :param body: content body
        :type body: bytes
        :param json: json body
        :type json: object
        :rtype: Response



.. autoclass:: aioconsul.api.Response

    .. attribute:: method

        str - Called method

    .. attribute:: url

        str - Called URL

    .. attribute:: status

        int - Status of response

    .. attribute:: headers

        dict - Headers of response

    .. attribute:: body

        object - Decoded response's body


.. autoclass:: aioconsul.api.ConflictError
.. autoclass:: aioconsul.api.ConsulError
.. autoclass:: aioconsul.api.NotFound
.. autoclass:: aioconsul.api.UnauthorizedError

.. _Consul: https://www.consul.io
