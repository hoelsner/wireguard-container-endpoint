"""
test rules API endpoints
"""
import pytest
from fastapi.testclient import TestClient

import models


@pytest.mark.usefixtures("disable_os_level_commands")
class TestIpv4FilterRuleApi:
    """
    Test Ipv4FilterRuleModel API
    """
    list_api_endpoint = "/api/rules/filters/ipv4"
    detail_api_endpoint = "/api/rules/filters/ipv4/{instance_id}"

    async def test_get_endpoint(self, test_client: TestClient, clean_db):
        """
        get get API endpoint
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        for e in range(4000, 4050):
            await models.Ipv4FilterRuleModel.create(
                policy_rule_list=prl,
                protocol=models.FilterProtocolEnum.TCP,
                dst_port_number=e
            )

        # fetch through API
        response = await test_client.get(self.list_api_endpoint)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 50

        response = await test_client.get(self.detail_api_endpoint.format(instance_id=data[0]["instance_id"]))
        assert response.status_code == 200, response.text

        json_data = response.json()
        assert json_data == {
            "instance_id": data[0]["instance_id"],
            "policy_rule_list": {
                "instance_id": data[0]["policy_rule_list"]["instance_id"],
                "name": "foo"
            },
            "src_network": "0.0.0.0/0",
            "dst_network": "0.0.0.0/0",
            "except_src": False,
            "except_dst": False,
            "protocol": "tcp",
            "action": "DROP",
            "table": "FORWARD",
            "dst_port_number": 4000
        }

    async def test_crud(self, test_client: TestClient, clean_db):
        """
        test CRUD operations on API endpoint
        """
        prl = await models.PolicyRuleListModel.create(name="foo")

        # create through API
        response = await test_client.post(self.list_api_endpoint, json={
            "policy_rule_list_id": str(prl.instance_id),
            "except_src": False,
            "except_dst": False,
            "protocol": "udp",
            "action": "DROP",
            "table": "FORWARD",
            "dst_port_number": 8443
        })
        assert response.status_code == 200, response.text

        # fetch created entry from DB
        data = response.json()
        frm = await models.Ipv4FilterRuleModel.get(
            instance_id=data["instance_id"]
        )

        # update through API (just change the port number)
        response = await test_client.put(self.detail_api_endpoint.format(instance_id=frm.instance_id), json={
            "dst_port_number": 8444
        })
        assert response.status_code == 200, response.text
        frm = await models.Ipv4FilterRuleModel.get(
            instance_id=data["instance_id"]
        )
        assert frm.dst_port_number == 8444

        # delete through API
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id=frm.instance_id))
        assert response.status_code == 200
        assert await models.Ipv4FilterRuleModel.all().count() == 0

    async def test_delete_with_invalid_id(self, test_client: TestClient):
        """test delete with invalid id"""
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id="NotExist"))
        assert response.status_code == 404

    async def test_invalid_input_on_generic_field(self, test_client: TestClient):
        """
        test post call with invalid data
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        response = await test_client.post(self.list_api_endpoint, json={
            "policy_rule_list_id": str(prl.instance_id),
            "protocol": "tcp",
            "action": "DROP",
            "table": "FORWARD",
            "dst_port_number": 8555555
        })
        assert response.status_code == 422, response.text

        data = response.json()
        assert data == {
            "detail": [
                {
                    "msg": "dst_port_number: Value should be less or equal to 65535",
                    "body": "ValidationError"
                }
            ]
        }

    async def test_invalid_input_on_enum_field(self, test_client: TestClient):
        """
        test post call with invalid data
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        response = await test_client.post(self.list_api_endpoint, json={
            "policy_rule_list_id": str(prl.instance_id),
            "protocol": "FailVal",
            "action": "DROP",
            "table": "FORWARD",
            "dst_port_number": 443
        })
        assert response.status_code == 422, response.text

        data = response.json()
        assert data == {
            "detail": [{"msg": "'FailVal' is not a valid FilterProtocolEnum", "body": "ValidationError"}]
        }


@pytest.mark.usefixtures("disable_os_level_commands")
class TestIpv6FilterRuleApi:
    """
    Test Ipv6FilterRuleModel API
    """
    list_api_endpoint = "/api/rules/filters/ipv6"
    detail_api_endpoint = "/api/rules/filters/ipv6/{instance_id}"

    async def test_get_endpoint(self, test_client: TestClient, clean_db):
        """
        get get API endpoint
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        for e in range(4000, 4050):
            await models.Ipv6FilterRuleModel.create(
                policy_route_list=prl,
                protocol=models.FilterProtocolEnum.TCP,
                dst_port_number=e
            )

        # fetch through API
        response = await test_client.get(self.list_api_endpoint)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 50

        response = await test_client.get(self.detail_api_endpoint.format(instance_id=data[0]["instance_id"]))
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data == data[0]

    async def test_crud(self, test_client: TestClient, clean_db):
        """
        test CRUD operations on API endpoint
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        # create through API
        response = await test_client.post(self.list_api_endpoint, json={
            "policy_rule_list_id": str(prl.instance_id),
            "except_src": False,
            "except_dst": False,
            "protocol": "udp",
            "action": "DROP",
            "table": "FORWARD",
            "dst_port_number": 8443
        })
        assert response.status_code == 200, response.text

        # fetch created entry from DB
        data = response.json()
        frm = await models.Ipv6FilterRuleModel.get(
            instance_id=data["instance_id"]
        )

        # update through API (just change the port number)
        response = await test_client.put(self.detail_api_endpoint.format(instance_id=frm.instance_id), json={
            "dst_port_number": 8444
        })
        assert response.status_code == 200, response.text
        frm = await models.Ipv6FilterRuleModel.get(
            instance_id=data["instance_id"]
        )
        assert frm.dst_port_number == 8444

        # delete through API
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id=frm.instance_id))
        assert response.status_code == 200
        assert await models.Ipv6FilterRuleModel.all().count() == 0

    async def test_delete_with_invalid_id(self, test_client: TestClient):
        """test delete with invalid ID"""
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id="doesntExist"))
        assert response.status_code == 404

    async def test_invalid_input_on_generic_field(self, test_client: TestClient):
        """
        test post call with invalid data
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        response = await test_client.post(self.list_api_endpoint, json={
            "policy_rule_list_id": str(prl.instance_id),
            "protocol": "tcp",
            "action": "DROP",
            "table": "FORWARD",
            "dst_port_number": 8555555
        })
        assert response.status_code == 422, response.text

        data = response.json()
        assert data == {
            "detail": [
                {"msg": "dst_port_number: Value should be less or equal to 65535", "body": "ValidationError"}
            ]
        }, response.text

    async def test_invalid_input_on_enum_field(self, test_client: TestClient):
        """
        test post call with invalid data
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        response = await test_client.post(self.list_api_endpoint, json={
            "policy_rule_list_id": str(prl.instance_id),
            "protocol": "FailVal",
            "action": "DROP",
            "table": "FORWARD",
            "dst_port_number": 443
        })
        assert response.status_code == 422, response.text

        data = response.json()
        assert data == {
            "detail": [
                {"msg": "'FailVal' is not a valid FilterProtocolEnum", "body": "ValidationError"}
            ]
        }, response.text


@pytest.mark.usefixtures("disable_os_level_commands")
class TestIpv4NatRuleApi:
    """
    Test Ipv4NatRuleModel API
    """
    list_api_endpoint = "/api/rules/nat/ipv4"
    detail_api_endpoint = "/api/rules/nat/ipv4/{instance_id}"

    async def test_get_endpoint(self, test_client: TestClient, clean_db):
        """
        get get API endpoint
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        for e in range(4000, 4050):
            await models.Ipv4NatRuleModel.create(
                policy_rule_list=prl,
                target_interface=f"eth{e}"
            )

        # fetch through API
        response = await test_client.get(self.list_api_endpoint)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 50

        response = await test_client.get(self.detail_api_endpoint.format(instance_id=data[0]["instance_id"]))
        assert response.status_code == 200

        resp_data = response.json()
        assert resp_data == data[0]

    async def test_crud(self, test_client: TestClient, clean_db):
        """
        test CRUD operations on API endpoint
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        # create through API
        response = await test_client.post(self.list_api_endpoint, json={
            "policy_rule_list_id": str(prl.instance_id),
            "target_interface": "eth0"
        })
        assert response.status_code == 200, response.text

        # fetch created entry from DB
        data = response.json()
        frm = await models.Ipv4NatRuleModel.get(
            instance_id=data["instance_id"]
        )

        # update through API (just change the port number)
        response = await test_client.put(self.detail_api_endpoint.format(instance_id=frm.instance_id), json={
            "target_interface": "eth3"
        })
        assert response.status_code == 200, response.text
        frm = await models.Ipv4NatRuleModel.get(
            instance_id=data["instance_id"]
        )
        assert frm.target_interface == "eth3"
        obj = await frm.policy_rule_list.get()
        assert obj.instance_id == prl.instance_id, "relation to parent object missing"

        # delete through API
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id=frm.instance_id))
        assert response.status_code == 200
        assert await models.Ipv4NatRuleModel.all().count() == 0

    async def test_delete_with_invalid_id(self, test_client: TestClient):
        """test delete with invalid ID"""
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id="NotExist"))
        assert response.status_code == 404

    async def test_invalid_input_on_generic_field(self, test_client: TestClient):
        """
        test post call with invalid data
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        response = await test_client.post(self.list_api_endpoint, json={
            "policy_rule_list_id": str(prl.instance_id),
            "target_interface": "dfghevhirbviebnjbnetjbntjbnjrtenbjtrnbjrn tbgrjgn jrtbrtbtr"
        })
        assert response.status_code == 422, response.text

        data = response.json()
        assert data == {
            "detail":[
                {
                    "loc":["body","target_interface"],
                    "msg":"ensure this value has at most 32 characters",
                    "type":"value_error.any_str.max_length",
                    "ctx":{"limit_value":32}
                }
            ],
            "body":{
                "policy_rule_list_id": str(prl.instance_id),
                "target_interface":"dfghevhirbviebnjbnetjbntjbnjrtenbjtrnbjrn tbgrjgn jrtbrtbtr"
            }
        }, response.text


@pytest.mark.usefixtures("disable_os_level_commands")
class TestIpv6NatRuleApi:
    """
    Test Ipv6NatRuleModel API
    """
    list_api_endpoint = "/api/rules/nat/ipv6"
    detail_api_endpoint = "/api/rules/nat/ipv6/{instance_id}"

    async def test_get_endpoint(self, test_client: TestClient, clean_db):
        """
        get get API endpoint
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        for e in range(4000, 4050):
            await models.Ipv6NatRuleModel.create(
                policy_rule_list=prl,
                target_interface=f"eth{e}"
            )

        # fetch through API
        response = await test_client.get(self.list_api_endpoint)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 50

        response = await test_client.get(self.detail_api_endpoint.format(instance_id=data[0]["instance_id"]))
        assert response.status_code == 200

        resp_data = response.json()
        assert resp_data == data[0]

    async def test_crud(self, test_client: TestClient, clean_db):
        """
        test CRUD operations on API endpoint
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        # create through API
        response = await test_client.post(self.list_api_endpoint, json={
            "policy_rule_list_id": str(prl.instance_id),
            "target_interface": "eth0"
        })
        assert response.status_code == 200, response.text

        # fetch created entry from DB
        data = response.json()
        frm = await models.Ipv6NatRuleModel.get(
            instance_id=data["instance_id"]
        )

        # update through API (just change the port number)
        response = await test_client.put(self.detail_api_endpoint.format(instance_id=frm.instance_id), json={
            "target_interface": "eth3"
        })
        assert response.status_code == 200, response.text
        frm = await models.Ipv6NatRuleModel.get(
            instance_id=data["instance_id"]
        )
        assert frm.target_interface == "eth3"
        obj = await frm.policy_rule_list.get()
        assert obj.instance_id == prl.instance_id, "relation to parent object missing"

        # delete through API
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id=frm.instance_id))
        assert response.status_code == 200
        assert await models.Ipv6NatRuleModel.all().count() == 0

    async def test_delete_with_invalid_id(self, test_client: TestClient):
        """test delete with invalid id"""
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id="Not Found"))
        assert response.status_code == 404


@pytest.mark.usefixtures("disable_os_level_commands")
class TestPolicyRuleList:
    """
    Test PolicyRuleList API
    """
    list_api_endpoint = "/api/rules/policy_rule_list"
    detail_api_endpoint = "/api/rules/policy_rule_list/{instance_id}"

    async def test_get_endpoint(self, test_client: TestClient, clean_db):
        """
        get get API endpoint
        """
        for e in range(4000, 4050):
            await models.PolicyRuleListModel.create(
                name="foo{e}"
            )

        # fetch through API
        response = await test_client.get(self.list_api_endpoint)
        assert response.status_code == 200, response.text

        data = response.json()
        assert len(data) == 50

        response = await test_client.get(self.detail_api_endpoint.format(instance_id=data[0]["instance_id"]))
        assert response.status_code == 200

        resp_data = response.json()
        assert resp_data == data[0]

    async def test_crud(self, test_client: TestClient, clean_db):
        """
        test CRUD operations on API endpoint
        """
        # create through API
        response = await test_client.post(self.list_api_endpoint, json={
            "name": "foo"
        })
        assert response.status_code == 200, response.text
        assert await models.PolicyRuleListModel.all().count() == 1

        # fetch created entry from DB
        data = response.json()
        frm = await models.PolicyRuleListModel.get(
            instance_id=data["instance_id"]
        )

        # update through API (just change the port number)
        response = await test_client.put(self.detail_api_endpoint.format(instance_id=frm.instance_id), json={
            "name": "foo2"
        })
        assert response.status_code == 200, response.text
        assert await models.PolicyRuleListModel.all().count() == 1

        frm = await models.PolicyRuleListModel.get(
            instance_id=data["instance_id"]
        )
        assert frm.name == "foo2"

        # delete through API
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id=frm.instance_id))
        assert await models.PolicyRuleListModel.all().count() == 0

    async def test_delete_with_invalid_id(self, test_client: TestClient):
        """test delete with invalid id"""
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id="Not Found"))
        assert response.status_code == 404
