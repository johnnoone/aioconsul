Client reference
================

.. currentmodule:: aioconsul.client

.. autoclass:: aioconsul.client.Consul
    :no-members:
    :no-undoc-members:
    :no-inherited-members:

    .. attribute:: Consul.address

        Address of the agent.

        See :attr:`aioconsul.api.API.address`

    .. attribute:: Consul.consistency

        See :attr:`aioconsul.api.API.consistency`

    .. attribute:: Consul.token

        Token of the agent.

        See :attr:`aioconsul.api.API.token`

    .. attribute:: api

        Expose :class:`aioconsul.api.API`

    .. attribute:: acl

        See :ref:`acl_endpoint` for examples
        and :class:`aioconsul.client.ACLEndpoint` for implementation.

    .. attribute:: agent

        See :ref:`agent_endpoint` for examples
        and :class:`aioconsul.client.AgentEndpoint` for implementation.

    .. attribute:: catalog

        See :ref:`catalog_endpoint` for examples
        and :class:`aioconsul.client.CatalogEndpoint` for implementation.

    .. attribute:: checks

        See :ref:`checks_endpoint` for examples
        and :class:`aioconsul.client.ChecksEndpoint` for implementation.

    .. attribute:: coordinate

        See :ref:`coordinate_endpoint` for examples
        and :class:`aioconsul.client.CoordinateEndpoint` for implementation.

    .. attribute:: event

        See :ref:`event_endpoint` for examples
        and :class:`aioconsul.client.EventEndpoint` for implementation.

    .. attribute:: health

        See :ref:`health_endpoint` for examples
        and :class:`aioconsul.client.HealthEndpoint` for implementation.

    .. attribute:: kv

        See :ref:`kv_endpoint` for examples
        and :class:`aioconsul.client.KVEndpoint` for implementation

        About transactional operations,
        see :ref:`kv_operations_endpoint` for examples
        and :class:`aioconsul.client.KVOperations` for transaction.

    .. attribute:: members

        See :ref:`members_endpoint` for examples
        See :class:`aioconsul.client.MembersEndpoint` for implementation.

    .. attribute:: operator

        See :ref:`operator_endpoint` for examples
        and :class:`aioconsul.client.OperatorEndpoint` for implementation.

    .. attribute:: query

        See :ref:`query_endpoint` for examples
        and :class:`aioconsul.client.QueryEndpoint` for implementation.

    .. attribute:: services

        See :ref:`services_endpoint` for examples
        and :class:`aioconsul.client.ServicesEndpoint` for implementation.

    .. attribute:: session

        See :ref:`session_endpoint` for examples
        and :class:`aioconsul.client.SessionEndpoint` for implementation.

    .. attribute:: status

        See :ref:`status_endpoint` for examples
        and :class:`aioconsul.client.StatusEndpoint` for implementation.
