

def prepare_node(data):
    """Prepare node for catalog endpoint

    Parameters:
        data (Union[str, dict]): Node ID or node definition
    Returns:
        Tuple[str, dict]: where first is ID and second is node definition

    Extract from /v1/health/service/<service>::

        {
            "Node": {
                "Node": "foobar",
                "Address": "10.1.10.12",
                "TaggedAddresses": {
                    "lan": "10.1.10.12",
                    "wan": "10.1.10.12"
                }
            },
            "Service": {...},
            "Checks": [...]
        }
    """
    if not data:
        return None, {}

    if isinstance(data, str):
        return data, {}

    # from /v1/health/service/<service>
    if all(field in data for field in ("Node", "Service", "Checks")):
        return data["Node"]["Node"], data["Node"]

    result = {}
    if "ID" in data:
        result["Node"] = data["ID"]
    for k in ("Datacenter", "Node", "Address",
              "TaggedAddresses", "Service",
              "Check", "Checks"):
        if k in data:
            result[k] = data[k]
    if list(result) == ["Node"]:
        return result["Node"], {}
    return result.get("Node"), result


def prepare_service(data):
    """Prepare service for catalog endpoint

    Parameters:
        data (Union[str, dict]): Service ID or service definition
    Returns:
        Tuple[str, dict]: str is ID and dict is service

    Transform ``/v1/health/state/<state>``::

        {
            "Node": "foobar",
            "CheckID": "service:redis",
            "Name": "Service 'redis' check",
            "Status": "passing",
            "Notes": "",
            "Output": "",
            "ServiceID": "redis1",
            "ServiceName": "redis"
        }

    to::

        {
            "ID": "redis1",
            "Service": "redis"
        }

    Extract from /v1/health/service/<service>::

        {
            "Node": {...},
            "Service": {
                "ID": "redis1",
                "Service": "redis",
                "Tags": None,
                "Address": "10.1.10.12",
                "Port": 8000
            },
            "Checks": [...]
        }

    """
    if not data:
        return None, {}

    if isinstance(data, str):
        return data, {}

    # from /v1/health/service/<service>
    if all(field in data for field in ("Node", "Service", "Checks")):
        return data["Service"]["ID"], data["Service"]

    # from /v1/health/checks/<service>
    # from /v1/health/node/<node>
    # from /v1/health/state/<state>
    # from /v1/catalog/service/<service>
    if all(field in data for field in ("ServiceName", "ServiceID")):
        return data["ServiceID"], {
            "ID": data["ServiceID"],
            "Service": data["ServiceName"],
            "Tags": data.get("ServiceTags"),
            "Address": data.get("ServiceAddress"),
            "Port": data.get("ServicePort"),
        }

    if list(data) == ["ID"]:
        return data["ID"], {}

    result = {}
    if "Name" in data:
        result["Service"] = data["Name"]

    for k in ("Service", "ID", "Tags", "Address", "Port"):
        if k in data:
            result[k] = data[k]
    return result.get("ID"), result


def prepare_check(data):
    """Prepare check for catalog endpoint

    Parameters:
        data (Object or ObjectID): Check ID or check definition
    Returns:
        Tuple[str, dict]: where first is ID and second is check definition
    """
    if not data:
        return None, {}

    if isinstance(data, str):
        return data, {}

    result = {}
    if "ID" in data:
        result["CheckID"] = data["ID"]
    for k in ("Node", "CheckID", "Name", "Notes", "Status", "ServiceID"):
        if k in data:
            result[k] = data[k]
    if list(result) == ["CheckID"]:
        return result["CheckID"], {}
    return result.get("CheckID"), result
