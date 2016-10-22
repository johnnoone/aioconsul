import pytest
from aioconsul import Consul
from collections.abc import Mapping, Sequence


@pytest.mark.asyncio
async def test_endpoint(client):
    assert repr(client.acl) == "<ACLEndpoint(%r)>" % str(client.address)


@pytest.mark.asyncio
async def test_acl(client):
    acl = {
        "Name": "my-app-token",
        "Type": "client",
        "Rules": ""
    }
    response = await client.acl.create(acl)
    assert isinstance(response, Mapping)
    assert "ID" in response
    acl.update(response)

    info, meta = await client.acl.info(acl)
    assert isinstance(info, Mapping)
    assert "ID" in info
    assert acl["ID"] == info["ID"]
    assert "Index" in meta
    assert "KnownLeader" in meta
    assert "LastContact" in meta

    clone, meta = await client.acl.clone(acl)
    assert isinstance(clone, Mapping)
    assert clone["ID"] != acl["ID"]
    assert "Index" in meta
    assert "KnownLeader" in meta
    assert "LastContact" in meta

    clone["Name"] = "foobar"
    response = await client.acl.update(clone)
    assert "ID" in response
    assert response["ID"] == clone["ID"]

    items, meta = await client.acl.items()

    replication = await client.acl.replication()
    assert "Enabled" in replication

    destroyed = await client.acl.destroy(acl)
    assert destroyed is True

    destroyed = await client.acl.destroy(clone)
    assert destroyed is True


rule_dict = {
    'key': {
        '': {
            'policy': 'read'
        },
        'private/': {
            'policy': 'deny'
        }
    }
}

rule_hcl = """
    key "" {
        policy = "read"
    }
    key "private/" {
        policy = "deny"
    }
"""

rule_json = """{
  "key": {
    "": {
      "policy": "read"
    },
    "private/": {
      "policy": "deny"
    }
  }
}"""

@pytest.mark.asyncio
@pytest.mark.parametrize("input, expected", [
    (rule_hcl, rule_dict),
    (rule_json, rule_dict),
    (rule_dict, rule_dict)
])
async def test_rules(client, input, expected):
    token = {
        "Name": "my-app-token",
        "Type": "client",
        "Rules": input
    }
    token_id = await client.acl.create(token)
    token.update(token_id)

    info, meta = await client.acl.info(token)
    assert info["Rules"] == expected
