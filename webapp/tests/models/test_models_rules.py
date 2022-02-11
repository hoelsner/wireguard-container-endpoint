"""
test rules models
"""
# pylint: disable=unused-argument
import pytest
from fastapi.testclient import TestClient

import models


class TestIpv4FilterRuleModel:
    """
    Test Ipv4FilterRuleModel model
    """
    async def test_rule_with_port(self, test_client: TestClient, clean_db):
        """test rule with port filter
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            protocol=models.FilterProtocolEnum.TCP,
            dst_port_number=3000
        )

        exp_rule = "iptable -A FORWARD -i %i -p tcp -dport 3000 -j DROP"
        assert frm.to_iptables_rule() == exp_rule
        assert frm.__str__() == exp_rule

        exp_rule = "iptable -A FORWARD -i eth0 -p tcp -dport 3000 -j DROP"
        assert frm.to_iptables_rule(intf_name="eth0") == exp_rule

        exp_rule = "iptable -D FORWARD -i %i -p tcp -dport 3000 -j DROP"
        assert frm.to_iptables_rule(drop_rule=True) == exp_rule

    async def test_rule_with_ip_addresses(self, test_client: TestClient, clean_db):
        """test rule with IPv4 network filter
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24"
        )

        exp_rule = "iptable -A FORWARD -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j DROP"
        assert frm.to_iptables_rule() == exp_rule

    async def test_ignore_rule(self, test_client: TestClient, clean_db):
        """test rule with IPv4 network filter
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl
        )

        assert frm.to_iptables_rule() == ""

    async def test_rule_with_ip_addresses_and_action(self, test_client: TestClient, clean_db):
        """test rule with IPv4 network filter with action
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            action=models.IpTableActionEnum.ACCEPT
        )

        exp_rule = "iptable -A FORWARD -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j ACCEPT"
        assert frm.to_iptables_rule() == exp_rule

    async def test_rule_with_ip_addresses_and_table(self, test_client: TestClient, clean_db):
        """test rule with IPv4 network filter with table
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            table=models.IpTableNameEnum.INPUT
        )

        exp_rule = "iptable -A INPUT -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j DROP"
        assert frm.to_iptables_rule() == exp_rule

    async def test_rule_with_ip_addresses_and_except(self, test_client: TestClient, clean_db):
        """test rule with except IPv4 network filter
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            except_src=True,
            except_dst=True
        )

        exp_rule = "iptable -A FORWARD -i %i ! -s 192.168.1.0/24 ! -d 192.168.2.0/24 -j DROP"
        assert frm.to_iptables_rule() == exp_rule


class TestIpv6FilterRuleModel:
    """
    Test Ipv6FilterRuleModel model
    """
    async def test_rule_with_ip_addresses(self, test_client: TestClient, clean_db):
        """test rule with IPv4 network filter
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv6FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="DB8:0::/64",
            dst_network="DB8:1::/64"
        )

        exp_rule = "ip6table -A FORWARD -i %i -s DB8:0::/64 -d DB8:1::/64 -j DROP"
        assert frm.to_iptables_rule() == exp_rule
        assert frm.__str__() == exp_rule

        # fetch through API
        response = await test_client.get("/api/rules/filters/ipv6")
        assert response.status_code == 200, response.text

        data = response.json()
        assert len(data) == 1
        assert data[0]["instance_id"] == str(frm.instance_id), response.text


class TestIpv4NatRuleModel:
    """
    Test TestIpv4NatRuleModel model
    """
    async def test_nat_rule_output(self, test_client: TestClient, clean_db):
        """test the generation of a NAT rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4NatRuleModel.create(
            policy_rule_list=prl
        )

        exp_rule = "iptable -A POSTROUTING -t nat -o eth0 -j MASQUERADE"
        assert frm.to_iptables_rule() == exp_rule
        assert frm.__str__() == exp_rule

    async def test_nat_rule_output_with_interface_name(self, test_client: TestClient, clean_db):
        """test the generation of a NAT rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4NatRuleModel.create(
            policy_rule_list=prl,
            target_interface="eth8"
        )

        exp_rule = "iptable -A POSTROUTING -t nat -o eth8 -j MASQUERADE"
        assert frm.to_iptables_rule(intf_name="foo") == exp_rule, "This must not change anything on the iptables command"
        assert frm.__str__() == exp_rule


class TestIpv6NatRuleModel:
    """
    Test TestIpv6NatRuleModel model
    """
    async def test_nat_rule_output(self, test_client: TestClient, clean_db):
        """test the generation of a NAT rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv6NatRuleModel.create(
            policy_rule_list=prl
        )

        exp_rule = "ip6table -A POSTROUTING -t nat -o eth0 -j MASQUERADE"
        assert frm.to_iptables_rule() == exp_rule
        assert frm.__str__() == exp_rule

    async def test_nat_rule_output_with_interface_name(self, test_client: TestClient, clean_db):
        """test the generation of a NAT rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv6NatRuleModel.create(
            policy_rule_list=prl,
            target_interface="eth8"
        )

        exp_rule = "ip6table -A POSTROUTING -t nat -o eth8 -j MASQUERADE"
        assert frm.to_iptables_rule(intf_name="foo") == exp_rule, "This must not change anything on the iptables command"
        assert frm.__str__() == exp_rule


class TestPolicyRuleListModel:
    """
    Test PolicyRuleList model
    """
    async def _create_test_data(self, prl: models.PolicyRuleListModel):
        """create test data for the class"""
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            protocol=models.FilterProtocolEnum.TCP,
            dst_port_number=3000
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24"
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            action=models.IpTableActionEnum.ACCEPT
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            table=models.IpTableNameEnum.INPUT
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            except_src=True,
            except_dst=True
        )
        await models.Ipv6FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="DB8:0::/64",
            dst_network="DB8:1::/64"
        )
        await models.Ipv4NatRuleModel.create(
            policy_rule_list=prl,
            target_interface="eth1"
        )
        await models.Ipv6NatRuleModel.create(
            policy_rule_list=prl,
            target_interface="eth8"
        )

    async def test_basics(self, test_client: TestClient, clean_db):
        """test the generation of a NAT rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")

        amount = await models.PolicyRuleListModel.all()
        assert len(amount) == 1

    async def test_iptable_rule_list(self, test_client: TestClient, clean_db):
        """test full iptable rule list
        """
        prl = await models.PolicyRuleListModel.create(name="test_policy")
        await self._create_test_data(prl)

        expected_create_result = [
            "iptable -A FORWARD -i %i -p tcp -dport 3000 -j DROP",
            "iptable -A FORWARD -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j DROP",
            "iptable -A FORWARD -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j ACCEPT",
            "iptable -A INPUT -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j DROP",
            "iptable -A FORWARD -i %i ! -s 192.168.1.0/24 ! -d 192.168.2.0/24 -j DROP",
            "ip6table -A FORWARD -i %i -s DB8:0::/64 -d DB8:1::/64 -j DROP",
            "iptable -A POSTROUTING -t nat -o eth1 -j MASQUERADE",
            "ip6table -A POSTROUTING -t nat -o eth8 -j MASQUERADE"
        ]
        expected_drop_result = [
            "iptable -D FORWARD -i %i -p tcp -dport 3000 -j DROP",
            "iptable -D FORWARD -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j DROP",
            "iptable -D FORWARD -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j ACCEPT",
            "iptable -D INPUT -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j DROP",
            "iptable -D FORWARD -i %i ! -s 192.168.1.0/24 ! -d 192.168.2.0/24 -j DROP",
            "ip6table -D FORWARD -i %i -s DB8:0::/64 -d DB8:1::/64 -j DROP",
            "iptable -D POSTROUTING -t nat -o eth1 -j MASQUERADE",
            "ip6table -D POSTROUTING -t nat -o eth8 -j MASQUERADE"
        ]

        result = await prl.to_iptables_list(intf_name="%i", drop_rule=False)
        assert expected_create_result == result

        result = await prl.to_iptables_list(intf_name="%i", drop_rule=True)
        assert expected_drop_result == result

    async def test_ipv4_iptable_rule_list(self, test_client: TestClient, clean_db):
        """test ipv4 iptable rule list
        """
        prl = await models.PolicyRuleListModel.create(name="test_policy")
        await self._create_test_data(prl)

        expected_create_result_ipv4 = [
            "iptable -A FORWARD -i %i -p tcp -dport 3000 -j DROP",
            "iptable -A FORWARD -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j DROP",
            "iptable -A FORWARD -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j ACCEPT",
            "iptable -A INPUT -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j DROP",
            "iptable -A FORWARD -i %i ! -s 192.168.1.0/24 ! -d 192.168.2.0/24 -j DROP",
            "iptable -A POSTROUTING -t nat -o eth1 -j MASQUERADE"
        ]
        expected_drop_result_ipv4 = [
            "iptable -D FORWARD -i %i -p tcp -dport 3000 -j DROP",
            "iptable -D FORWARD -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j DROP",
            "iptable -D FORWARD -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j ACCEPT",
            "iptable -D INPUT -i %i -s 192.168.1.0/24 -d 192.168.2.0/24 -j DROP",
            "iptable -D FORWARD -i %i ! -s 192.168.1.0/24 ! -d 192.168.2.0/24 -j DROP",
            "iptable -D POSTROUTING -t nat -o eth1 -j MASQUERADE"
        ]
        result = await prl.to_ipv4_iptables_list(intf_name="%i", drop_rule=False)
        assert expected_create_result_ipv4 == result

        result = await prl.to_ipv4_iptables_list(intf_name="%i", drop_rule=True)
        assert expected_drop_result_ipv4 == result

    async def test_ipv6_iptable_rule_list(self, test_client: TestClient, clean_db):
        """test ipv6 iptable rule list
        """
        prl = await models.PolicyRuleListModel.create(name="test_policy")
        await self._create_test_data(prl)

        expected_create_result_ipv6 = [
            "ip6table -A FORWARD -i %i -s DB8:0::/64 -d DB8:1::/64 -j DROP",
            "ip6table -A POSTROUTING -t nat -o eth8 -j MASQUERADE"
        ]
        expected_drop_result_ipv6 = [
            "ip6table -D FORWARD -i %i -s DB8:0::/64 -d DB8:1::/64 -j DROP",
            "ip6table -D POSTROUTING -t nat -o eth8 -j MASQUERADE"
        ]
        result = await prl.to_ipv6_iptables_list(intf_name="%i", drop_rule=False)
        assert expected_create_result_ipv6 == result

        result = await prl.to_ipv6_iptables_list(intf_name="%i", drop_rule=True)
        assert expected_drop_result_ipv6 == result
