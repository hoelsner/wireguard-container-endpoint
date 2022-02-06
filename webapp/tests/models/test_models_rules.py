"""
test rules models
"""
import pytest
from fastapi.testclient import TestClient

import models


class TestIpv4FilterRuleModel:
    """
    Test Ipv4FilterRuleModel model
    """
    list_api_endpoint = "/api/rules/filters/ipv4"
    detail_api_endpoint = "/api/rules/filters/ipv4/{pk}"

    async def test_rule_with_port(self, test_client: TestClient):
        """test rule with port filter"""
        frm = await models.Ipv4FilterRuleModel.create(
            protocol=models.FilterProtocolEnum.TCP,
            dst_port_number=3000
        )

        exp_rule = "iptable -A FORWARD -i %i -p tcp -dport 3000 -j DROP"
        assert frm.to_iptables_rule() == exp_rule

        exp_rule = "iptable -A FORWARD -i eth0 -p tcp -dport 3000 -j DROP"
        assert frm.to_iptables_rule(intf_name="eth0") == exp_rule

        exp_rule = "iptable -D FORWARD -i %i -p tcp -dport 3000 -j DROP"
        assert frm.to_iptables_rule(drop_rule=True) == exp_rule

        # fetch through API
        response = test_client.get(self.list_api_endpoint)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["instance_id"] == str(frm.instance_id)
