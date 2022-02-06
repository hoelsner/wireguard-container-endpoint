"""
test rules API endpoints
"""
import pytest
from fastapi.testclient import TestClient

import models


class TestIpv4FilterRuleApi:
    """
    Test Ipv4FilterRuleModel API
    """
    list_api_endpoint = "/api/rules/filters/ipv4"
    detail_api_endpoint = "/api/rules/filters/ipv4/{instance_id}"

    async def test_get_endpoint(self, test_client: TestClient):
        """
        get get API endpoint
        """
        for e in range(4000, 4050):
            frm = await models.Ipv4FilterRuleModel.create(
                protocol=models.FilterProtocolEnum.TCP,
                dst_port_number=e
            )

        # fetch through API
        response = test_client.get(self.list_api_endpoint)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 50

        # cleanup
        await models.Ipv4FilterRuleModel.all().delete()

    async def test_crud(self, test_client: TestClient):
        """
        test CRUD operations on API endpoint
        """
        # create through API
        response = test_client.post(self.list_api_endpoint, json={
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
        response = test_client.put(self.detail_api_endpoint.format(instance_id=frm.instance_id), json={
            "dst_port_number": 8444
        })
        assert response.status_code == 200, response.text
        frm = await models.Ipv4FilterRuleModel.get(
            instance_id=data["instance_id"]
        )
        assert frm.dst_port_number == 8444

        # delete through API
        response = test_client.delete(self.detail_api_endpoint.format(instance_id=frm.instance_id))
        assert await models.Ipv4FilterRuleModel.all().count() == 0

    async def test_invalid_input_on_generic_field(self, test_client: TestClient):
        """
        test post call with invalid data
        """
        response = test_client.post(self.list_api_endpoint, json={
            "protocol": "tcp",
            "action": "DROP",
            "table": "FORWARD",
            "dst_port_number": 8555555
        })
        assert response.status_code == 422, response.text

        data = response.json()
        assert data == {"detail": [{"msg": "dst_port_number: Value should be less or equal to 65535", "body": "ValidationError"}]}

    async def test_invalid_input_on_enum_field(self, test_client: TestClient):
        """
        test post call with invalid data
        """
        response = test_client.post(self.list_api_endpoint, json={
            "protocol": "FailVal",
            "action": "DROP",
            "table": "FORWARD",
            "dst_port_number": 443
        })
        assert response.status_code == 422, response.text

        data = response.json()
        assert data == {"detail": [{"msg": "'FailVal' is not a valid FilterProtocolEnum", "body": "ValidationError"}]}
